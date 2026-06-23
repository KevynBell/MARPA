from pathlib import Path

import torch

from model import AttentionLanguageModel
from tokenizer import load_text, build_tokenizer
from agent_router import route_prompt
from tools import (
    plan_goal,
    execute_goal_tool,
)
from memory_manager import (
    load_observations,
    load_project_notes,
    load_permanent_memory,
)
from llm_backend import ask_local_model
from question_manager import (
    create_question,
    list_open_questions,
    get_oldest_open_question,
    answer_question,
)

checkpoint_path = Path("models/marpa_transformer_stack_v1.pth")

text = load_text()
chars, stoi, itos, encode, decode = build_tokenizer(text)
vocab_size = len(chars)

model = AttentionLanguageModel(vocab_size)
model.load_state_dict(torch.load(checkpoint_path))
model.eval()

print("MARPA loaded.")
print("Type 'quit' to exit.\n")

conversation_history = []
max_history_items = 10

project_notes = load_project_notes()
observations = load_observations()
permanent_memory = load_permanent_memory()

while True:
    prompt = input("You: ")

    if prompt.lower() in ["/quit", "quit", "exit"]:
        break

    if prompt.lower().startswith("/plan "):
        goal = prompt[6:].strip()
        print("\nMARPA:")
        print(plan_goal(goal))
        print()
        continue

    if prompt.lower().startswith("/execute "):
        goal = prompt[9:].strip()

        print("\nMARPA:")
        print(execute_goal_tool(goal))
        print()

        continue
    
    if prompt.lower() == "/observations":
        print("\nMARPA:")
        print(load_observations())
        print()
        continue
    
    if prompt.lower().startswith("/curious "):
        topic = prompt[9:].strip()
        print("\nMARPA:")
        print(create_question(topic))
        print()
        continue

    if prompt.lower() in ["/questions", "show questions", "what questions do you have?"]:
        print("\nMARPA:")
        print(list_open_questions())
        print()
        continue

    if prompt.lower() in ["/ask", "do you have any questions?", "do you have any questions for me?"]:
        print("\nMARPA:")
        print(get_oldest_open_question())
        print()
        continue

    if prompt.lower().startswith("/answer "):
        parts = prompt.split(" ", 2)

        if len(parts) < 3:
            print("\nMARPA:")
            print("Use: /answer Q1 your answer here")
            print()
            continue

        question_id = parts[1].strip()
        answer = parts[2].strip()

        print("\nMARPA:")
        print(answer_question(question_id, answer))
        print()
        continue
    
    if prompt.lower() == "what did i just ask?":
        last_user_messages = [
            item for item in conversation_history
            if item.startswith("User:")
        ]

        if last_user_messages:
            print(
                last_user_messages[-1]
                .replace("User:", "")
                .strip()
            )
        else:
            print("You have not asked anything yet.")

        continue    

    routed_response = route_prompt(prompt)

    if routed_response is not None:
        print("\nMARPA:")
        print(routed_response)
        print()

        conversation_history.append(f"User: {prompt}")
        conversation_history.append(f"MARPA: {routed_response}")

        if len(conversation_history) > max_history_items:
            conversation_history = conversation_history[-max_history_items:]

        continue
    
# Model fallback line
    conversation_context = "\n".join(conversation_history[-6:])

    conversation_prompt = f"""
    You are MARPA, the Memory-Augmented Reasoning and Planning Assistant.

    You are a local AI development assistant being built by Kevyn.
    You help with software projects, debugging, memory, planning, and learning.

    MARPA Identity and Project Notes:
    {project_notes}

    Permanent Memory:
    {permanent_memory}

    Recent Observations:
    {observations}

    Recent Conversation:
    {conversation_context}

    User:
    {prompt}

    MARPA:
    """

    output = ask_local_model(conversation_prompt)
    
    print("\nMARPA:")
    print(output)

    conversation_history.append(f"User: {prompt}")
    conversation_history.append(f"MARPA: {output}")

    if len(conversation_history) > max_history_items:
        conversation_history = conversation_history[-max_history_items:]
    
    print()