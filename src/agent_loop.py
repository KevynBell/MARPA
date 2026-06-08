from planner import create_plan
from project_search import search_project_files
from file_tools import read_project_file


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


def execute_goal(goal):

    plan = think(goal)

    action_result = act(goal)

    observation = observe(action_result)

    next_file = choose_next_action(action_result)

    next_result = ""

    if next_file:
        next_result = read_project_file(next_file)

    return f"""
=== PLAN ===

{plan}

=== ACTION RESULT ===

{action_result}

=== OBSERVATION ===

{observation}

=== NEXT ACTION ===

Read: {next_file}

=== RESULT ===

{next_result}
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