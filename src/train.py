import torch
import torch.nn as nn
from torch.nn import functional as F
from pathlib import Path


# Hyperparameters
block_size = 8
batch_size = 4
max_iters = 3000
eval_interval = 300
learning_rate = 1e-2

checkpoint_path = Path("models/marpa_bigram_v1.pth")
load_existing_model = True


# Load Dataset
with open("data/tiny_text.txt", "r", encoding="utf-8") as f:
    text = f.read()


# Vocabulary
chars = sorted(list(set(text)))
vocab_size = len(chars)


# Character ↔ Integer Mapping
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for i, ch in enumerate(chars)}


# Encoder / Decoder
def encode(s):
    return [stoi[c] for c in s]

def decode(l):
    return ''.join([itos[i] for i in l])


# Encode dataset
data = torch.tensor(encode(text), dtype=torch.long)


# Train / Validation
n = int(0.9 * len(data))
train_data = data[:n]
val_data = data[n:]


# Create training batches
def get_batch(split):
    
    data = train_data if split == 'train' else val_data
    
    ix = torch.randint(len(data) - block_size, (batch_size,))
    
    x = torch.stack([data[i:i + block_size] for i in ix])
    y = torch.stack([data[i + 1:i + block_size + 1] for i in ix])
    
    return x, y

# Bigram Language Model
class BigramLanguageModel(nn.Module):
    
    def __init__(self, vocab_size):
        super().__init__()
        
        # Lookup table
        self.token_embedding_table = nn.Embedding(vocab_size, vocab_size)
        
        
    def forward(self, idx, targets=None):
        
        # Get Predictions
        
        logits = self.token_embedding_table(idx)
        
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
            
            logits, loss = self(idx)
            
            logits = logits[:, -1, :]
            
            probs = F.softmax(logits, dim=-1)
            
            idx_next = torch.multinomial(probs, num_samples=1)
            
            idx = torch.cat((idx, idx_next), dim=1)
            
        return idx
    
    
# Create model
model = BigramLanguageModel(vocab_size)

if load_existing_model and checkpoint_path.exists():
    model.load_state_dict(torch.load(checkpoint_path))
    print("Loaded existing MARPA checkpoint.")
else:
    print("Starting MARPA from scratch.")


# Optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)


# Training Loop
for iter in range(max_iters):

    xb, yb = get_batch('train')

    logits, loss = model(xb, yb)
    
    optimizer.zero_grad(set_to_none=True)
    
    loss.backward()
    
    optimizer.step()
    
    if iter % eval_interval == 0:
        print(f"step {iter}: Loss = {loss.item():.4f}")
        
torch.save(model.state_dict(), checkpoint_path)
print(f"Saved MARPA checkpoint to {checkpoint_path}")


# Generate text
context = torch.zeros((1, 1), dtype=torch.long)

generated_text = decode (
    model.generate(context, max_new_tokens=100)[0].tolist()
)

print("\nGenerated Text:")
print(generated_text)