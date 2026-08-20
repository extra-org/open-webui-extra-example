"""Shared Open WebUI HTTP call helper.

Tools call `request(...)` and get back `(data, error)`. `error` is None on
success, otherwise a string that says *what actually went wrong* — status code
plus the server's own message — so the model can decide whether to fix its
arguments and retry, or tell the user the real reason.

NAIVE FIRST PASS — every call goes out with one admin API key, regardless of
who is asking. That means any user who can reach this chat can perform any
admin action Open WebUI allows: create accounts, delete users, anything. Do
not deploy this. The next commit replaces it with the caller's own identity.
"""

import os

import requests

OPEN_WEBUI_URL = os.environ["OPEN_WEBUI_URL"]
API_KEY = os.environ["OPEN_WEBUI_API_KEY"]

TIMEOUT = 10


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
    url = f"{OPEN_WEBUI_URL}{path}"
    try:
        response = requests.request(
            method,
            url,
            headers={
                "Authorization": f"Bearer {API_KEY}",
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
            401: " The API key is missing, invalid, or expired.",
            403: " The API key lacks permission for this operation.",
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
