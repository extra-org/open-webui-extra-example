"""Self-check: a run starts with a freshly issued token, or it does not start.

Run: python -m plugins.hooks.test_run_token
"""

from agent_engine.runtime.hooks import AuthContext, HookInvocation, RunContext

from plugins.hooks import run_token
from plugins.hooks.run_token import NoRunCredential, RunTokenHook


def _event(ctx):
    return HookInvocation(hook_point="on_run_start", payload=ctx)


class FakeResponse:
    def __init__(self, ok, payload=None):
        self.ok = ok
        self._payload = payload

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


def _raise(*a, **k):
    raise run_token.requests.exceptions.ConnectionError("down")


def _refuses(event, hook):
    try:
        hook.on_run_start(event)
    except NoRunCredential:
        return True
    return False


def main():
    hook = RunTokenHook()
    caller = RunContext(run_id="r1", auth_context=AuthContext(inbound_access_token="short"))

    # Every run trades its inbound token for a fresh one, whatever is left on it.
    run_token.requests.get = lambda *a, **k: FakeResponse(True, {"token": "long"})
    assert hook.on_run_start(_event(caller)).auth_context.inbound_access_token == "long"

    # No fresh token means no run: the alternative is a partial run that dies at
    # an unpredictable tool call, having already changed things.
    for failure in (lambda *a, **k: FakeResponse(False),
                    lambda *a, **k: FakeResponse(True, {}),
                    lambda *a, **k: FakeResponse(True),
                    _raise):
        run_token.requests.get = failure
        assert _refuses(_event(caller), hook), failure

    # Nothing to trade is refused before any call goes out.
    attempts = []
    run_token.requests.get = lambda *a, **k: attempts.append(a) or FakeResponse(True, {})
    assert _refuses(_event(RunContext(run_id="r2")), hook)
    assert attempts == []

    print("ok")


if __name__ == "__main__":
    main()
