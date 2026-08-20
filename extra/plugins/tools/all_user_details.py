from plugins.tools._owui import request

# ponytail: the API returns ~23 fields per user (profile images, bio, settings blobs).
# Only these are ever used for identifying or acting on a user — widen if a tool needs more.
FIELDS = ("id", "email", "username", "role", "name", "group_ids")


def all_user_details(
    page: int = 1,
    order_by: str = "created_at",
    direction: str = "asc",
):
    """List Open WebUI users."""
    data, error = request(
        "GET",
        "/api/v1/users/",
        params={"page": page, "order_by": order_by, "direction": direction},
    )
    if error:
        return {"error": f"Failed to list users. {error}"}

    users = data.get("users", []) if isinstance(data, dict) else data
    slim = [{f: u.get(f) for f in FIELDS} for u in users]

    if isinstance(data, dict):
        return {**data, "users": slim}
    return slim
