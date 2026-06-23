from pathlib import Path
from datetime import datetime

MEMORY_DIR = Path("memory")
CONVERSATION_LOG_PATH = MEMORY_DIR / "conversation_log.txt"


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
        existing_text = observations_path.read_text(encoding="utf-8")

        if observation in existing_text:
            return "Observation already exists."

    with open(observations_path, "a", encoding="utf-8") as file:
        file.write(f"\n{observation}\n")

    return "Observation saved."

def load_permanent_memory():
    memory_path = MEMORY_DIR / "permanent_memory.txt"

    if not memory_path.exists():
        return ""

    return memory_path.read_text(encoding="utf-8")


def save_memory(memory_item):
    memory_path = MEMORY_DIR / "permanent_memory.txt"

    with open(memory_path, "a", encoding="utf-8") as file:
        file.write(f"\n{memory_item}\n")

    return "Memory saved."

def load_conversation_log():
    if not CONVERSATION_LOG_PATH.exists():
        return "MARPA Conversation Log"

    return CONVERSATION_LOG_PATH.read_text(encoding="utf-8")


def save_conversation_exchange(user_prompt, marpa_response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = f"""

[{timestamp}]
User: {user_prompt}
MARPA: {marpa_response}
"""

    with open(CONVERSATION_LOG_PATH, "a", encoding="utf-8") as file:
        file.write(entry)

    return "Conversation saved."


def load_recent_conversation(limit=12):
    text = load_conversation_log()
    lines = [
        line for line in text.splitlines()
        if line.startswith("User:") or line.startswith("MARPA:")
    ]

    return "\n".join(lines[-limit:])