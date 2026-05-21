from pathlib import Path
from datetime import datetime

import torch

from model import AttentionLanguageModel, block_size
from tokenizer import load_text, build_tokenizer

text = load_text()

chars, stoi, itos, encode, decode = build_tokenizer(text)
vocab_size = len(chars)

data = torch.tensor(encode(text), dtype=torch.long)

n = int(0.9 * len(data))
train_data = data[:n]
val_data = data[n:]

# ----------------------------
# Hyperparameters
# ----------------------------
batch_size = 8
max_iters = 5000
eval_interval = 500
learning_rate = 1e-3
eval_iters = 100


checkpoint_path = Path("models/marpa_transformer_stack_v1.pth")
load_existing_model = True
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_path = log_dir / f"training_run_{run_id}.txt"

torch.manual_seed(1337)


# ----------------------------
# Batching
# ----------------------------
def get_batch(split):
    data_source = train_data if split == "train" else val_data

    ix = torch.randint(len(data_source) - block_size, (batch_size,))

    x = torch.stack([data_source[i:i + block_size] for i in ix])
    y = torch.stack([data_source[i + 1:i + block_size + 1] for i in ix])

    return x, y

@torch.no_grad()
def estimate_loss():
    out = {}
    model.eval()

    for split in ["train", "val"]:
        losses = torch.zeros(eval_iters)

        for k in range(eval_iters):
            x, y = get_batch(split)
            logits, loss = model(x, y)
            losses[k] = loss.item()

        out[split] = losses.mean()

    model.train()
    return out


# ----------------------------
# Create / Load Model
# ----------------------------
model = AttentionLanguageModel(vocab_size)

if load_existing_model and checkpoint_path.exists():
    model.load_state_dict(torch.load(checkpoint_path))
    print("Loaded existing MARPA attention checkpoint.")
else:
    print("Starting MARPA attention model from scratch.")

optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

# ----------------------------
# Training Loop
# ----------------------------
for step in range(max_iters):

    if step % eval_interval == 0:
        losses = estimate_loss()
        message = (
            f"step {step}: "
            f"train loss = {losses['train']:.4f}, "
            f"val loss = {losses['val']:.4f}"
        )

        print(message)

        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")

    xb, yb = get_batch("train")

    logits, loss = model(xb, yb)

    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

# ----------------------------
# Save Model
# ----------------------------
torch.save(model.state_dict(), checkpoint_path)
print(f"Saved MARPA checkpoint to {checkpoint_path}")

# ----------------------------
# Generate Text
# ----------------------------
context = torch.zeros((1, 1), dtype=torch.long)

generated_text = decode(
    model.generate(context, max_new_tokens=500)[0].tolist()
)

print("\nGenerated Text:")
print(generated_text)

with open(log_path, "a", encoding="utf-8") as log_file:
    log_file.write("\nGenerated Text:\n")
    log_file.write(generated_text)
    log_file.write("\n")