from pathlib import Path

import torch

from model import AttentionLanguageModel
from tokenizer import load_text, build_tokenizer
from memory_manager import (
    load_project_notes,
    load_observations,
    save_observation
)
from tools import show_help, show_notes, show_status, show_memory


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
observations = load_observations()
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
    
    if prompt.lower() == "/observations":
        print(load_observations())
        continue
    
    if prompt.lower() == "/memory":
        print(show_memory())
        continue
    
    if prompt.lower().startswith("/observe "):
        observation = prompt[9:].strip()
        print(save_observation(observation))
        observations = load_observations()
        continue
    
    
    full_prompt = f"""
    Project Memory:
    {project_notes}
    
    Observations:
    {observations}
    
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