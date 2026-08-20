"""Shared Open WebUI HTTP call helper.

Tools call `request(...)` and get back `(data, error)`. `error` is None on
success, otherwise a string that says *what actually went wrong* — status code
plus the server's own message — so the model can decide whether to fix its
arguments and retry, or tell the user the real reason.

Every call goes out as the person who asked, using the credential on the current
run's context. No shared key to fall back on: that fallback is what would let
anyone reaching the chat act as an admin. Open WebUI stays the authority.
"""

import os

import requests
from agent_engine.runtime.hooks import current_run_context

# No default: a deployment missing this should fail at startup, not quietly
# talk to whatever is on localhost.
OPEN_WEBUI_URL = os.environ["OPEN_WEBUI_URL"]

TIMEOUT = 10

NO_CREDENTIAL = (
    "No Open WebUI credential for this request, so it was not sent. Report that "
    "the action could not be performed and say which steps did complete."
)


def _caller_token() -> str | None:
    ctx = current_run_context.get()
    if ctx is None or ctx.auth_context is None:
        return None
    return ctx.auth_context.inbound_access_token


def _server_message(response) -> str:
    """Best-effort extraction of Open WebUI's error text."""
    try:
        body = response.json()
    except ValueError:
        return response.text.strip()[:300] or "(empty response body)"
    if isinstance(body, dict):
        for key in ("detail", "message", "error"):
            if body.get(key):
                return str(body[key])[:300]
    return str(body)[:300]


def request(method: str, path: str, **kwargs):
    """Call the Open WebUI API. Returns (data, error).

    data  — parsed JSON, or None when the body is empty / on failure.
    error — None on success, else a descriptive message for the model.
    """
    token = _caller_token()
    if token is None:
        return None, NO_CREDENTIAL

    url = f"{OPEN_WEBUI_URL}{path}"
    try:
        response = requests.request(
            method,
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=TIMEOUT,
            **kwargs,
        )
    except requests.exceptions.Timeout:
        return None, f"Open WebUI did not respond within {TIMEOUT}s ({method} {path})."
    except requests.exceptions.ConnectionError as e:
        return None, f"Could not reach Open WebUI at {OPEN_WEBUI_URL} ({method} {path}): {e}."
    except requests.exceptions.RequestException as e:
        return None, f"Request to {method} {path} failed: {e}."

    if not response.ok:
        hint = {
            401: " The credential expired mid-run. Do not retry; report what"
            " completed and what did not, and ask the user to send the request again.",
            403: " This user is not allowed to do that. Say so plainly; do not"
            " look for another way round it.",
            404: " The target does not exist — check the id you passed.",
            409: " That resource already exists.",
        }.get(response.status_code, "")
        return None, (
            f"Open WebUI returned HTTP {response.status_code} "
            f"for {method} {path}: {_server_message(response)}.{hint}"
        )

    if not response.content:
        return None, None
    try:
        return response.json(), None
    except ValueError:
        return response.text, None
