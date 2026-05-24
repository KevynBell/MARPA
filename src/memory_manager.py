from pathlib import Path

MEMORY_DIR = Path("memory")


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