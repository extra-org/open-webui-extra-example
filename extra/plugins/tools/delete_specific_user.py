from plugins.tools._owui import request


def delete_specific_user(user_id: str):
    """Delete an Open WebUI user by their ID."""
    data, error = request("DELETE", f"/api/v1/users/{user_id}")
    if error:
        return {"error": f"Failed to delete user '{user_id}'. {error}"}

    return {"message": f"Deleted user '{user_id}'.", "data": data}
