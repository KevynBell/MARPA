from pathlib import Path

import torch

from model import AttentionLanguageModel
from tokenizer import load_text, build_tokenizer
from agent_router import route_prompt

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

while True:
    prompt = input("You: ")

    if prompt.lower() in ["/quit", "quit", "exit"]:
        break

    context = torch.tensor(
        [encode(prompt)],
        dtype=torch.long
    )

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

    output = decode(
        model.generate(
            context,
            max_new_tokens=300
        )[0].tolist()
    )

    if output.startswith(prompt):
        output = output[len(prompt):].strip()

    print("\nMARPA:")
    print(output)

    conversation_history.append(f"User: {prompt}")
    conversation_history.append(f"MARPA: {output}")

    if len(conversation_history) > max_history_items:
        conversation_history = conversation_history[-max_history_items:]
    
    print()