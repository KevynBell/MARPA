from pathlib import Path

TASKS_PATH = Path("memory/tasks.txt")


def create_plan(goal):
    plan = [
        f"Goal: {goal}",
        "",
        "Plan:",
        "1. Define the desired outcome.",
        "2. Identify the current state.",
        "3. Break the goal into small tasks.",
        "4. Complete the first task.",
        "5. Test the result.",
        "6. Record observations.",
        "7. Decide the next improvement.",
    ]

    return "\n".join(plan)


def save_plan(goal):
    plan = create_plan(goal)

    with open(TASKS_PATH, "a", encoding="utf-8") as file:
        file.write("\n\n")
        file.write(plan)

    return plan