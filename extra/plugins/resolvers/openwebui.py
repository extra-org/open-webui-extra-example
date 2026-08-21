"""What the router is told it can route to, decided per caller.

The routing section used to be fixed text naming admin_management to everyone.
That was already untrue for most people: admin_management is protected, so for
a non-admin the router is handed no such destination at all. The prompt
described a door the model would then find missing, and the model has nothing
but the prompt to go on — so it would announce administrative help, try to
delegate, and come back empty.

`{{admin_routing}}` in prompts/openwebui_orchestrator/orchestrator.md is
replaced with one of the two blocks below before the model ever sees it.
This is not the access control — plugins/access.py is, and it stands on its
own. This only keeps what the router *believes* in step with what it can
actually reach.
"""

from plugins._identity import caller_is_admin

ADMIN_DESTINATIONS = """\
**admin_management** is currently the only destination. It handles \
administration of this Open WebUI instance: user accounts, groups, and \
membership.

- Administrative request → route to `admin_management`.
- Anything else → there is no agent for it yet. Say so plainly instead of \
forcing a route."""

NO_DESTINATIONS = """\
There are no destinations available for this person, so there is nothing to \
route to. Explain what this assistant is, and say plainly that you cannot \
carry out administrative work — never as something that could be arranged \
later, approved, or escalated."""


class Resolver:
    def admin_routing(self, ctx: dict) -> str:
        return ADMIN_DESTINATIONS if caller_is_admin() else NO_DESTINATIONS
