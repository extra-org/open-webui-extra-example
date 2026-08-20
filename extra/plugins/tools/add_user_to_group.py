from plugins.tools._owui import request


def add_user_to_group(group_id: str, user_ids: list[str]) -> dict:
    """
    Add one or more users to an Open WebUI group.

    Args:
        group_id: The ID of the group.
        user_ids: List of user IDs to add to the group.
    """
    data, error = request(
        "POST",
        f"/api/v1/groups/id/{group_id}/users/add",
        json={"user_ids": user_ids},
    )
    if error:
        return {"error": f"Failed to add users {user_ids} to group '{group_id}'. {error}"}

    return {
        "message": f"Added users {user_ids} to group '{group_id}'.",
        "data": data,
    }
