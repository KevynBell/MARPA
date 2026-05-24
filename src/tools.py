from pathlib import Path
from memory_manager import (
    load_project_notes, 
    load_observations,
    load_permanent_memory
)
from file_tools import read_project_file

from retrieval import retrieve_memory

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
/observe <observation>  Save an observation to memory
/observations  Show all saved observations
/memory   Show project notes and observations
/history Show current session conversation history
/search <query>  Search MARPA memory
/remember <text>  Save permanent memory
/recall           Show permanent memory
/read <path>  Read a project file
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

def show_memory():
    notes = load_project_notes()
    observations = load_observations()

    return f"""
MARPA Memory

Project Notes:
{notes}

Observations:
{observations}
"""

def search_memory(query):
    results = retrieve_memory(query)

    if not results:
        return "No matching memory found."

    return f"""
Memory Search Results:

{results}
"""

def show_permanent_memory():
    memory = load_permanent_memory()

    if not memory:
        return "No permanent memory found."

    return memory

def read_file(file_path):
    return read_project_file(file_path)