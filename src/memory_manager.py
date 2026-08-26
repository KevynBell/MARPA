import json
import re
from datetime import datetime
from pathlib import Path


MEMORY_DIR = Path("memory")
USERS_DIR = MEMORY_DIR / "users"

DEFAULT_USER_ID = "kevyn"


def sanitize_user_id(user_id: str) -> str:
    """
    Convert a user ID into a safe directory name.
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


def get_user_dir(
    user_id: str = DEFAULT_USER_ID,
) -> Path:
    safe_user_id = sanitize_user_id(user_id)

    user_dir = USERS_DIR / safe_user_id
    user_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return user_dir


def get_user_conversation_log_path(
    user_id: str = DEFAULT_USER_ID,
) -> Path:
    return (
        get_user_dir(user_id)
        / "conversation_log.jsonl"
    )


def get_legacy_conversation_log_path(
    user_id: str = DEFAULT_USER_ID,
) -> Path:
    return (
        get_user_dir(user_id)
        / "conversation_log.txt"
    )


def get_user_memory_path(
    user_id: str = DEFAULT_USER_ID,
) -> Path:
    return (
        get_user_dir(user_id)
        / "permanent_memory.txt"
    )


def load_project_notes():
    notes_path = MEMORY_DIR / "project_notes.txt"

    if not notes_path.exists():
        return "No project notes found."

    return notes_path.read_text(
        encoding="utf-8"
    )


def load_observations():
    observations_path = (
        MEMORY_DIR / "observations.txt"
    )

    if not observations_path.exists():
        return ""

    return observations_path.read_text(
        encoding="utf-8"
    )


def save_observation(observation):
    observations_path = (
        MEMORY_DIR / "observations.txt"
    )

    if observations_path.exists():
        existing_text = observations_path.read_text(
            encoding="utf-8"
        )

        if observation in existing_text:
            return "Observation already exists."

    with open(
        observations_path,
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            f"\n{observation}\n"
        )

    return "Observation saved."


def load_permanent_memory(
    user_id: str = DEFAULT_USER_ID,
):
    memory_path = get_user_memory_path(
        user_id
    )

    if not memory_path.exists():
        return ""

    return memory_path.read_text(
        encoding="utf-8"
    )


def save_memory(
    memory_item,
    user_id: str = DEFAULT_USER_ID,
):
    memory_path = get_user_memory_path(
        user_id
    )

    with open(
        memory_path,
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            f"\n{memory_item}\n"
        )

    return "Memory saved."


def save_conversation_exchange(
    user_prompt,
    marpa_response,
    user_id: str = DEFAULT_USER_ID,
):
    safe_user_id = sanitize_user_id(
        user_id
    )

    conversation_log_path = (
        get_user_conversation_log_path(
            safe_user_id
        )
    )

    record = {
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "user_id": safe_user_id,
        "prompt": str(user_prompt),
        "response": str(marpa_response),
    }

    with open(
        conversation_log_path,
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )

    return "Conversation saved."


def load_conversation_records(
    user_id: str = DEFAULT_USER_ID,
):
    conversation_log_path = (
        get_user_conversation_log_path(
            user_id
        )
    )

    if not conversation_log_path.exists():
        return []

    records = []

    with open(
        conversation_log_path,
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(
            file,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)

            except json.JSONDecodeError:
                print(
                    "[MARPA memory] "
                    f"Skipping malformed JSONL "
                    f"record on line {line_number}."
                )
                continue

            if not isinstance(record, dict):
                continue

            if (
                "prompt" not in record
                or "response" not in record
            ):
                continue

            records.append(record)

    return records


def load_recent_conversation(
    limit=4,
    user_id: str = DEFAULT_USER_ID,
):
    records = load_conversation_records(
        user_id
    )

    recent_records = records[-limit:]

    conversation_parts = []

    for record in recent_records:
        prompt = str(
            record.get(
                "prompt",
                "",
            )
        )

        response = str(
            record.get(
                "response",
                "",
            )
        )

        conversation_parts.append(
            f"User: {prompt}\n"
            f"MARPA: {response}"
        )

    return "\n\n".join(
        conversation_parts
    )


def migrate_legacy_conversation_log(
    user_id: str = DEFAULT_USER_ID,
):
    """
    Convert the old text conversation log into JSONL.

    Existing JSONL data is left untouched.
    """
    safe_user_id = sanitize_user_id(
        user_id
    )

    legacy_path = (
        get_legacy_conversation_log_path(
            safe_user_id
        )
    )

    jsonl_path = (
        get_user_conversation_log_path(
            safe_user_id
        )
    )

    if (
        jsonl_path.exists()
        and jsonl_path.stat().st_size > 0
    ):
        return 0

    if not legacy_path.exists():
        return 0

    text = legacy_path.read_text(
        encoding="utf-8"
    )

    pattern = re.compile(
        r"""
        \[
        (?P<timestamp>
            \d{4}-\d{2}-\d{2}
            \s+
            \d{2}:\d{2}:\d{2}
        )
        \]
        \s*
        User:\s*
        (?P<prompt>.*?)
        \n
        MARPA:\s*
        (?P<response>.*?)
        (?=
            \n\s*
            \[
            \d{4}-\d{2}-\d{2}
            \s+
            \d{2}:\d{2}:\d{2}
            \]
            |
            \Z
        )
        """,
        re.DOTALL | re.VERBOSE,
    )

    records = []

    for match in pattern.finditer(text):
        records.append(
            {
                "timestamp": (
                    match.group(
                        "timestamp"
                    ).replace(
                        " ",
                        "T",
                    )
                ),
                "user_id": safe_user_id,
                "prompt": (
                    match.group(
                        "prompt"
                    ).strip()
                ),
                "response": (
                    match.group(
                        "response"
                    ).strip()
                ),
            }
        )

    if not records:
        return 0

    with open(
        jsonl_path,
        "w",
        encoding="utf-8",
    ) as file:
        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

    return len(records)
