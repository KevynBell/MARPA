from pathlib import Path

import torch

from model import AttentionLanguageModel
from tokenizer import load_text, build_tokenizer
from memory_manager import load_project_notes
from tools import show_help, show_notes, show_status


checkpoint_path = Path("models/marpa_transformer_stack_v1.pth")

text = load_text()
chars, stoi, itos, encode, decode = build_tokenizer(text)
vocab_size = len(chars)

model = AttentionLanguageModel(vocab_size)
model.load_state_dict(torch.load(checkpoint_path))
model.eval()

print("MARPA loaded.")
print("Type 'quit' to exit.\n")

project_notes = load_project_notes()
print("Project memory loaded.\n")

while True:
    prompt = input("You: ")
    
    if prompt.lower() == "/quit":
        break

    if prompt.lower() == "/help":
        print(show_help())
        continue

    if prompt.lower() == "/notes":
        print(show_notes())
        continue

    if prompt.lower() == "/status":
        print(show_status())
        continue
    
    full_prompt = f"""
    Project Memory:
    {project_notes}
    
    User:
    {prompt}
    
    Marpa:
    """

    context = torch.tensor(
        [encode(full_prompt)],
        dtype=torch.long
    )

    generated_tokens = model.generate(
        context,
        max_new_tokens=300
    )[0].tolist()

    new_tokens = generated_tokens[len(context[0]):]

    output = decode(new_tokens)

    print("\nMARPA:")
    print(output)
    print()