from copy import deepcopy

from plugins.tools._owui import request


DEFAULT_PERMISSIONS = {
    "workspace": {
        "models": False,
        "knowledge": False,
        "prompts": False,
        "tools": False,
        "skills": False,
        "models_import": False,
        "models_export": False,
        "prompts_import": False,
        "prompts_export": False,
        "tools_import": False,
        "tools_export": False,
        "skills_import": False,
        "skills_export": False,
    },
    "sharing": {
        "models": False,
        "public_models": False,
        "knowledge": False,
        "public_knowledge": False,
        "prompts": False,
        "public_prompts": False,
        "tools": False,
        "public_tools": False,
        "skills": False,
        "public_skills": False,
        "notes": False,
        "public_notes": False,
        "folders": False,
        "public_chats": False,
        "open_chats": False,
        "public_calendars": False,
    },
    "access_grants": {
        "allow_users": True,
        "allow_groups": True,
    },
    "chat": {
        "controls": True,
        "valves": True,
        "system_prompt": True,
        "params": True,
        "file_upload": True,
        "web_upload": True,
        "delete": True,
        "delete_message": True,
        "continue_response": True,
        "regenerate_response": True,
        "rate_response": True,
        "edit": True,
        "share": True,
        "export": True,
        "import": True,
        "stt": True,
        "tts": True,
        "call": True,
        "multiple_models": True,
        "temporary": True,
        "temporary_enforced": False,
    },
    "features": {
        "api_keys": False,
        "notes": True,
        "channels": True,
        "folders": True,
        "direct_tool_servers": False,
        "web_search": True,
        "image_generation": True,
        "code_interpreter": True,
        "memories": True,
        "automations": False,
        "calendar": True,
        "webhooks": False,
    },
    "settings": {
        "interface": True,
    },
}


def create_group(
    name: str,
    description: str = "Created via API",
) -> dict:
    """
    Create an Open WebUI group with default permissions.
    """

    data, error = request(
        "POST",
        "/api/v1/groups/create",
        json={
            "name": name,
            "description": description,
            "data": {"config": {"share": "members"}},
            "permissions": deepcopy(DEFAULT_PERMISSIONS),
        },
    )
    if error:
        return {"error": f"Failed to create group '{name}'. {error}"}

    return {"message": f"Created group '{name}'.", "data": data}
