from memory_manager import (
    load_project_notes,
    load_observations
)

def retrieve_memory(query):
    memory = []

    notes = load_project_notes()
    observations = load_observations()

    all_text = notes + "\n" + observations

    query_words = query.lower().split()

    for line in all_text.splitlines():
        line_lower = line.lower()

        if any(word in line_lower for word in query_words):
            memory.append(line)

    return "\n".join(memory[:10])