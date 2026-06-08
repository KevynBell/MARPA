from planner import create_plan
from project_search import search_project_files
from file_tools import read_project_file
from datetime import datetime
from pathlib import Path
from memory_manager import save_observation

AGENT_RUNS_PATH = Path("memory/agent_runs.txt")


def think(goal):
    return create_plan(goal)


def extract_search_query(goal):
    lowered = goal.lower()

    phrases_to_remove = [
        "find files related to",
        "find files about",
        "search files for",
        "find",
        "files",
        "related",
        "to",
        "about",
    ]

    query = lowered

    for phrase in phrases_to_remove:
        query = query.replace(phrase, "")

    return query.strip()


def act(goal):
    lowered = goal.lower()

    if "file" in lowered or "files" in lowered:
        query = extract_search_query(goal)
        return search_project_files(query)

    return "No action available."


def observe(result):
    if result == "No matching files found.":
        return "Action failed."

    return "Action completed."

def save_agent_run(report):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(AGENT_RUNS_PATH, "a", encoding="utf-8") as file:
        file.write("\n\n")
        file.write(f"Run Timestamp: {timestamp}\n")
        file.write(report)

    return report


def summarize_result(file_path, file_content):
    if not file_content:
        return "No content available to summarize."

    lines = file_content.splitlines()
    non_empty_lines = [
        line.strip()
        for line in lines
        if line.strip()
    ]

    preview = "\n".join(non_empty_lines[:8])

    return f"""
Summary:
Read {file_path}.
The file contains {len(non_empty_lines)} non-empty lines.

Preview of key content:
{preview}
"""


def choose_next_action(action_result):
    if action_result == "No matching files found.":
        return None

    files = action_result.splitlines()

    preferred_folders = [
        "memory/",
        "data/corpus_sources/",
        "src/",
    ]

    for folder in preferred_folders:
        for file in files:
            normalized_file = file.replace("\\", "/")

            if normalized_file.startswith(folder):
                return file

    if len(files) > 0:
        return files[0]

    return None


def create_execution_observation(goal, selected_file, observation):
    if observation != "Action completed.":
        return None

    return (
        f"MARPA executed the goal '{goal}', "
        f"selected '{selected_file}', and completed the action successfully."
    )


def execute_goal(goal):

    plan = think(goal)

    action_result = act(goal)

    observation = observe(action_result)

    next_file = choose_next_action(action_result)

    next_result = ""

    if next_file:
        next_result = read_project_file(next_file)

    summary = ""

    execution_observation = create_execution_observation(
    goal,
    next_file,
    observation
)

    if execution_observation:
        save_observation(execution_observation)

    if next_file:
        summary = summarize_result(next_file, next_result)

    report = f"""
=== MARPA ACTION REPORT ===

Goal:
{goal}

Planning Output:
{plan}

Actions Taken:
1. Searched project files for relevant matches.
2. Selected the most relevant file to inspect.
3. Read the selected file in the background.
4. Summarized the result.

Selected File:
{next_file}

Observation:
{observation}

{summary}
"""

    return save_agent_run(report)