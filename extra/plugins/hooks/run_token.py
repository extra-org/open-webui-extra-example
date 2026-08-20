"""Trade the caller's session token for one that outlives the run.

A run lasts minutes; an Open WebUI session token may have seconds left when it
starts, so carrying it straight through means long runs fail partway. Open WebUI
reissues on `GET /api/v1/auths/agent-chat/token` for whoever presents a valid
credential, so each run opens by asking for a fresh one.

Extra never signs Open WebUI tokens itself: it verifies, then asks. Open WebUI
stays the only issuer, which keeps an asymmetric signing key an option later.
"""

import dataclasses

import requests
from agent_engine.runtime.hooks import HookInvocation, RunContext

from plugins.tools._owui import OPEN_WEBUI_URL

TOKEN_URL = f"{OPEN_WEBUI_URL}/api/v1/auths/agent-chat/token"
TIMEOUT = 5


class NoRunCredential(RuntimeError):
    """No credential this run could act with, so it does not start."""


class RunTokenHook:
    def on_run_start(self, event: HookInvocation) -> RunContext:
        ctx = event.payload_as(RunContext)
        auth = ctx.auth_context
        if auth is None or not auth.inbound_access_token:
            raise NoRunCredential(
                "This request carries no Open WebUI credential. Sign in and try again."
            )
        fresh = self._reissue(auth.inbound_access_token)
        if fresh is None:
            # Falling back to the caller's own token would gamble on however
            # many seconds it has left, and fail somewhere unpredictable.
            raise NoRunCredential(
                f"Could not obtain a run credential from {TOKEN_URL}. Try again."
            )
        return ctx.replace(
            auth_context=dataclasses.replace(auth, inbound_access_token=fresh)
        )

    def _reissue(self, token: str) -> str | None:
        try:
            response = requests.get(
                TOKEN_URL,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                timeout=TIMEOUT,
            )
            if not response.ok:
                return None
            fresh = response.json().get("token")
        except (requests.exceptions.RequestException, ValueError):
            return None
        return fresh if isinstance(fresh, str) and fresh else None
