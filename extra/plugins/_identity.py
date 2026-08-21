"""Who counts as an admin — decided once, for everything that asks.

Two places ask, for different reasons: plugins/access.py decides whether
admin_management is reachable at all, and the openwebui resolver decides
whether the router's prompt mentions it. They have to give the same answer.
A prompt that offers a destination access control will not grant produces an
assistant that promises admin work and then cannot do it.

They read the caller's roles from different places, because they are handed
different things: the access plugin receives the run context already flattened
to a dict, while a resolver is handed the other resolvers' values and has to
reach for the run's ambient identity itself.
"""

from collections.abc import Iterable

from agent_engine.runtime.hooks import current_run_context

ADMIN_ROLE = "admin"


def is_admin(roles: Iterable[str]) -> bool:
    return ADMIN_ROLE in roles


def caller_is_admin() -> bool:
    """For code with no context argument in hand.

    No identity means not an admin: this is the same fail-closed answer the
    access plugin gives, and the run has already been refused earlier if it
    truly carries no credential (see plugins/hooks/run_token.py).
    """
    ctx = current_run_context.get()
    if ctx is None or ctx.auth_context is None:
        return False
    return is_admin(ctx.auth_context.roles)
