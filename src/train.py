from pathlib import Path

import torch
import torch.nn as nn
from torch.nn import functional as F

# ----------------------------
# Hyperparameters
# ----------------------------
batch_size = 8
block_size = 16
max_iters = 5000
eval_interval = 500
learning_rate = 1e-3
eval_iters = 100
n_embd = 64

checkpoint_path = Path("models/marpa_attention_v1.pth")
load_existing_model = True

torch.manual_seed(1337)

# ----------------------------
# Load dataset
# ----------------------------
with open("data/tiny_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

chars = sorted(list(set(text)))
vocab_size = len(chars)

stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for i, ch in enumerate(chars)}

def encode(s):
    return [stoi[c] for c in s]

def decode(tokens):
    return "".join([itos[i] for i in tokens])

data = torch.tensor(encode(text), dtype=torch.long)

n = int(0.9 * len(data))
train_data = data[:n]
val_data = data[n:]

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
# Self-Attention Head
# ----------------------------
class Head(nn.Module):
    """One self-attention head."""

    def __init__(self, head_size):
        super().__init__()

        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)

        self.register_buffer(
            "tril",
            torch.tril(torch.ones(block_size, block_size))
        )

    def forward(self, x):
        B, T, C = x.shape

        k = self.key(x)
        q = self.query(x)

        weights = q @ k.transpose(-2, -1) * C ** -0.5

        weights = weights.masked_fill(
            self.tril[:T, :T] == 0,
            float("-inf")
        )

        weights = F.softmax(weights, dim=-1)

        v = self.value(x)
        out = weights @ v

        return out

# ----------------------------
# MARPA Self-Attention Model
# ----------------------------
class AttentionLanguageModel(nn.Module):

    def __init__(self):
        super().__init__()

        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embedding_table = nn.Embedding(block_size, n_embd)

        self.sa_head = Head(n_embd)

        self.lm_head = nn.Linear(n_embd, vocab_size)

    def forward(self, idx, targets=None):
        B, T = idx.shape

        token_emb = self.token_embedding_table(idx)
        position_emb = self.position_embedding_table(torch.arange(T))

        x = token_emb + position_emb

        x = self.sa_head(x)

        logits = self.lm_head(x)

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape

            logits = logits.view(B * T, C)
            targets = targets.view(B * T)

            loss = F.cross_entropy(logits, targets)

        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):

            idx_cond = idx[:, -block_size:]

            logits, loss = self(idx_cond)

            logits = logits[:, -1, :]

            probs = F.softmax(logits, dim=-1)

            idx_next = torch.multinomial(probs, num_samples=1)

            idx = torch.cat((idx, idx_next), dim=1)

        return idx

# ----------------------------
# Create / Load Model
# ----------------------------
model = AttentionLanguageModel()

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
        print(
            f"step {step}: "
            f"train loss = {losses['train']:.4f}, "
            f"val loss = {losses['val']:.4f}"
        )

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