from plugins.tools._owui import request


def add_new_user(name: str, email: str, password: str, role: str = "user") -> dict:
    """Create a new Open WebUI user account. Requires a name, email, and password; role defaults to "user" (use "admin" for admin accounts)."""
    data, error = request(
        "POST",
        "/api/v1/auths/add",
        json={"name": name, "email": email, "password": password, "role": role},
    )
    if error:
        return {"error": f"Failed to create user '{email}'. {error}"}

    return {
        "message": f"Created user '{name}' ({email}) with role '{role}'.",
        "data": data,
    }
