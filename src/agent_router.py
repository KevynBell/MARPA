from tools import (
    search_memory,
    search_files,
    read_file,
    inspect_project_file,
    show_memory,
    show_status,
    plan_goal,
)


def route_prompt(prompt):
    lowered = prompt.lower().strip()

    if lowered.startswith("search memory for "):
        query = prompt[len("search memory for "):].strip()
        return search_memory(query)

    if lowered.startswith("search files for "):
        query = prompt[len("search files for "):].strip()
        return search_files(query)
    
    if lowered.startswith("plan "):
        goal = prompt[len("plan "):].strip()
        return plan_goal(goal)
    
    if "status" in lowered:
        return show_status()

    if "memory" in lowered or "remember" in lowered:
        return show_memory()

    if lowered.startswith("read file "):
        file_path = prompt[len("read file "):].strip()
        return read_file(file_path)

    if lowered.startswith("inspect "):
        query = prompt[len("inspect "):].strip()
        return inspect_project_file(query)

    return None