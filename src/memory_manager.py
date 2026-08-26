from datetime import datetime
from pathlib import Path
import re


MEMORY_DIR = Path("memory")
USERS_DIR = MEMORY_DIR / "users"

DEFAULT_USER_ID = "kevyn"


def sanitize_user_id(user_id: str) -> str:
    """
    Convert a user ID into a safe directory name.

    Only lowercase letters, numbers, hyphens, and underscores are allowed.
    """
    cleaned = user_id.strip().lower()

    if not cleaned:
        return DEFAULT_USER_ID

    if not re.fullmatch(r"[a-z0-9_-]+", cleaned):
        raise ValueError(
            "User ID may only contain lowercase letters, numbers, "
            "hyphens, and underscores."
        )

    return cleaned


def get_user_dir(user_id: str = DEFAULT_USER_ID) -> Path:
    safe_user_id = sanitize_user_id(user_id)
    user_dir = USERS_DIR / safe_user_id
    user_dir.mkdir(parents=True, exist_ok=True)

    return user_dir


def get_user_conversation_log_path(
    user_id: str = DEFAULT_USER_ID,
) -> Path:
    return get_user_dir(user_id) / "conversation_log.txt"


def get_user_memory_path(
    user_id: str = DEFAULT_USER_ID,
) -> Path:
    return get_user_dir(user_id) / "permanent_memory.txt"


def load_project_notes():
    notes_path = MEMORY_DIR / "project_notes.txt"

    if not notes_path.exists():
        return "No project notes found."

    return notes_path.read_text(
        encoding="utf-8"
    )


def load_observations():
    observations_path = MEMORY_DIR / "observations.txt"

    if not observations_path.exists():
        return ""

    return observations_path.read_text(
        encoding="utf-8"
    )


def save_observation(observation):
    observations_path = MEMORY_DIR / "observations.txt"

    if observations_path.exists():
        existing_text = observations_path.read_text(
            encoding="utf-8"
        )

        if observation in existing_text:
            return "Observation already exists."

    with open(observations_path, "a", encoding="utf-8") as file:
        file.write(f"\n{observation}\n")

    return "Observation saved."


def load_permanent_memory(
    user_id: str = DEFAULT_USER_ID,
):
    memory_path = get_user_memory_path(user_id)

    if not memory_path.exists():
        return ""

    return memory_path.read_text(
        encoding="utf-8"
    )


def save_memory(
    memory_item,
    user_id: str = DEFAULT_USER_ID,
):
    memory_path = get_user_memory_path(user_id)

    with open(memory_path, "a", encoding="utf-8") as file:
        file.write(f"\n{memory_item}\n")

    return "Memory saved."


def load_conversation_log(
    user_id: str = DEFAULT_USER_ID,
):
    conversation_log_path = get_user_conversation_log_path(
        user_id
    )

    if not conversation_log_path.exists():
        return "MARPA Conversation Log"

    return conversation_log_path.read_text(
        encoding="utf-8"
    )


def save_conversation_exchange(
    user_prompt,
    marpa_response,
    user_id: str = DEFAULT_USER_ID,
):
    conversation_log_path = get_user_conversation_log_path(
        user_id
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    entry = f"""

[{timestamp}]
User: {user_prompt}
MARPA: {marpa_response}
"""

    with open(
        conversation_log_path,
        "a",
        encoding="utf-8",
    ) as file:
        file.write(entry)

    return "Conversation saved."


def load_recent_conversation(
    limit=12,
    user_id: str = DEFAULT_USER_ID,
):
    text = load_conversation_log(user_id)

    lines = [
        line for line in text.splitlines()
        if line.startswith("User:")
        or line.startswith("MARPA:")
    ]

    return "\n".join(lines[-limit:])
