"""Hide admin_management from anyone who isn't an Open WebUI admin.

`protected: true` on admin_management (agents.yml) means the router calls
this before ever offering it as a candidate — a denied or missing role hides
the node, it does not fail the run. A non-admin's model never learns
admin_management exists, rather than being told no after asking for it.

`ctx` here is the plain dict the engine builds from RunContext.auth_context
(see docs/SIDECAR_CONTEXT_AUTH.md), not RunContext itself — no token, just
the claims already resolved from it. `roles` is only populated because
Open WebUI's /agent-chat/token endpoint now sends `role`, matched by this
deployment's AGENT_AUTH_CLAIM_ROLES=role (.env.example).
"""

from plugins._identity import is_admin


class AccessResolver:
    def can_access(self, ctx: dict, node_id: str) -> bool:
        return is_admin(ctx.get("auth", {}).get("roles", ()))
