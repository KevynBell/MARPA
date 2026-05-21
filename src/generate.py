from pathlib import Path

import torch

from model import AttentionLanguageModel
from tokenizer import load_text, build_tokenizer

checkpoint_path = Path("models/marpa_transformer_stack_v1.pth")

text = load_text()
chars, stoi, itos, encode, decode = build_tokenizer(text)
vocab_size = len(chars)

model = AttentionLanguageModel(vocab_size)
model.load_state_dict(torch.load(checkpoint_path))
model.eval()

print("MARPA loaded.")
print("Type 'quit' to exit.\n")

while True:
    prompt = input("You: ")

    if prompt.lower() == "quit":
        break

    context = torch.tensor(
        [encode(prompt)],
        dtype=torch.long
    )

    output = decode(
        model.generate(
            context,
            max_new_tokens=300
        )[0].tolist()
    )

    print("\nMARPA:")
    print(output)
    print()