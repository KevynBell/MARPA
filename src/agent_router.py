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
    
    if lowered.startswith("/read "):
        file_path = prompt[len("/read "):].strip()
        return read_file(file_path)
    
    if lowered.startswith("read file "):
        file_path = prompt[len("read file "):].strip()
        return read_file(file_path)

    if lowered.startswith("inspect "):
        query = prompt[len("inspect "):].strip()
        return inspect_project_file(query)
    
    if "status" in lowered:
        return show_status()

    if lowered in ["/memory", "show memory", "show your memory"]:
        return show_memory()
    
    if lowered in ["what is marpa?", "what is marpa"]:
        return (
            "MARPA is a Memory-Augmented Reasoning and Planning Assistant. "
            "It is being built as a local AI development assistant with memory, planning, tools, and project support."
        )

    if lowered in ["what can you do?", "what can you do"]:
        return (
            "I can search files, read files, inspect project files, save observations, remember information, "
            "plan tasks, and run simple agent actions."
        )

    return None