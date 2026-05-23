from pathlib import Path

CHECKPOINT_PATH = Path("models/marpa_transformer_stack_v1.pth")
CORPUS_PATH = Path("data/marpa_corpus_v1.txt")
PROJECT_NOTES_PATH = Path("memory/project_notes.txt")


def show_help():
    return """
MARPA Commands:
/help    Show available commands
/notes   Show project memory notes
/status  Show project status
/quit    Exit MARPA
"""


def show_notes():
    if not PROJECT_NOTES_PATH.exists():
        return "No project notes found."

    return PROJECT_NOTES_PATH.read_text(encoding="utf-8")


def show_status():
    checkpoint_status = "found" if CHECKPOINT_PATH.exists() else "missing"
    corpus_status = "found" if CORPUS_PATH.exists() else "missing"

    return f"""
MARPA Status:
Checkpoint: {checkpoint_status}
Corpus: {corpus_status}
Checkpoint path: {CHECKPOINT_PATH}
Corpus path: {CORPUS_PATH}
"""