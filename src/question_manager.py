from pathlib import Path
from datetime import datetime

QUESTIONS_PATH = Path("memory/questions.txt")


def load_questions():
    if not QUESTIONS_PATH.exists():
        return "MARPA Question Queue"

    return QUESTIONS_PATH.read_text(encoding="utf-8")


def get_next_question_id():
    text = load_questions()
    existing_ids = []

    for line in text.splitlines():
        if line.startswith("[Q"):
            id_part = line.split("]")[0]
            number = id_part.replace("[Q", "")

            if number.isdigit():
                existing_ids.append(int(number))

    if not existing_ids:
        return "Q1"

    return f"Q{max(existing_ids) + 1}"


def create_question(topic):
    question_id = get_next_question_id()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    question = (
        f"\n\n[{question_id}] [open]\n"
        f"Created: {timestamp}\n"
        f"Topic: {topic}\n"
        f"Question: What should I remember about {topic}?\n"
    )

    with open(QUESTIONS_PATH, "a", encoding="utf-8") as file:
        file.write(question)

    return (
        f"I created a question about {topic}.\n\n"
        f"{question_id}: What should I remember about {topic}?"
    )


def list_open_questions():
    text = load_questions()
    blocks = text.split("\n\n")
    open_questions = [
        block for block in blocks
        if "[open]" in block
    ]

    if not open_questions:
        return "I do not have any open questions right now."

    return "\n\n".join(open_questions)


def get_oldest_open_question():
    text = load_questions()
    blocks = text.split("\n\n")

    for block in blocks:
        if "[open]" in block:
            return block

    return "I do not have any open questions right now."


def answer_question(question_id, answer):
    text = load_questions()
    blocks = text.split("\n\n")
    updated_blocks = []
    found = False

    for block in blocks:
        clean_block = block.strip()

        if clean_block.startswith(f"[{question_id}]") and "[open]" in clean_block:
            clean_block = clean_block.replace("[open]", "[answered]")
            clean_block += f"\nAnswer: {answer}"
            found = True

        updated_blocks.append(clean_block)

    QUESTIONS_PATH.write_text(
        "\n\n".join(updated_blocks),
        encoding="utf-8"
    )

    if not found:
        return f"No open question found with ID {question_id}."

    return f"Saved answer for {question_id}."
