from plugins.tools._owui import request


def list_of_groups():
    """List all Open WebUI groups."""
    data, error = request("GET", "/api/v1/groups/")
    if error:
        return {"error": f"Failed to list groups. {error}"}

    return data
