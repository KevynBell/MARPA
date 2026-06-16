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

    context = torch.tensor(
        [encode(prompt)],
        dtype=torch.long
    )

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

    if prompt.lower() == "/observations":
        print("\nMARPA:")
        print(load_observations())
        print()
        continue

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