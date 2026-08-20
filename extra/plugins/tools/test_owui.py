"""Self-check: calls go out as the caller, and error paths surface the real
reason rather than a generic string.

Run: python -m plugins.tools.test_owui
"""

import requests
from agent_engine.runtime.hooks import AuthContext, RunContext, current_run_context

from plugins.tools import _owui
from plugins.tools.add_new_user import add_new_user
from plugins.tools.all_user_details import all_user_details

CALLER = RunContext(auth_context=AuthContext(inbound_access_token="caller-token"))


class FakeResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self.ok = status_code < 400
        self._payload = payload
        self.text = text
        self.content = text.encode() or (b"{}" if payload is not None else b"")

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


def _patch(fn):
    _owui.requests.request = fn


def main():
    original = requests.request

    # No credential: refused before the wire, not just in the message.
    sent = []
    _patch(lambda *a, **k: sent.append(a) or FakeResponse(200, {}))
    err = add_new_user("Dana", "dana@example.com", "pw")["error"]
    assert "not sent" in err and "could not be performed" in err, err
    assert sent == [], "a request went out with no credential"

    token = current_run_context.set(CALLER)

    # The caller's own credential authenticates the call.
    _patch(lambda *a, **k: sent.append(k["headers"]["Authorization"]) or FakeResponse(200, {}))
    all_user_details()
    assert sent == ["Bearer caller-token"], sent

    _patch(lambda *a, **k: FakeResponse(403, {"detail": "Not authorized"}))
    err = add_new_user("Dana", "dana@example.com", "pw")["error"]
    assert "403" in err and "Not authorized" in err and "not allowed" in err, err

    _patch(lambda *a, **k: FakeResponse(400, None, text="bad email format"))
    err = add_new_user("Dana", "not-an-email", "pw")["error"]
    assert "400" in err and "bad email format" in err, err

    def boom(*a, **k):
        raise requests.exceptions.ConnectionError("connection refused")

    _patch(boom)
    err = add_new_user("Dana", "dana@example.com", "pw")["error"]
    assert "Could not reach Open WebUI" in err and "connection refused" in err, err

    # success carries the server's own payload, not just a crafted sentence
    _patch(lambda *a, **k: FakeResponse(200, {"id": "abc", "role": "user"}))
    result = add_new_user("Dana", "dana@example.com", "pw")
    assert result["data"] == {"id": "abc", "role": "user"}, result
    assert result["message"].startswith("Created user 'Dana'"), result
    assert "error" not in result, result

    # the user list is trimmed to the identifying fields only
    fat_user = {
        "id": "3c8b", "email": "amit@test.com", "username": None,
        "role": "admin", "name": "amit", "profile_image_url": "data:image/png...",
        "bio": None, "settings": {"ui": {"version": "0.11.0"}},
        "group_ids": ["9f21"],
    }
    _patch(lambda *a, **k: FakeResponse(200, {"users": [fat_user], "total": 7}))
    result = all_user_details()
    assert result["total"] == 7, result
    assert result["users"] == [
        {"id": "3c8b", "email": "amit@test.com", "username": None,
         "role": "admin", "name": "amit", "group_ids": ["9f21"]}
    ], result

    current_run_context.reset(token)
    _owui.requests.request = original
    print("ok")


if __name__ == "__main__":
    main()
