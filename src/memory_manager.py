from pathlib import Path

MEMORY_DIR = Path("memory")


def load_project_notes():
    notes_path = MEMORY_DIR / "project_notes.txt"

    if not notes_path.exists():
        return "No project notes found."

    return notes_path.read_text(
        encoding="utf-8"
    )