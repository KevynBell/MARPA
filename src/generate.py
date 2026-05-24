from pathlib import Path

import torch

from model import AttentionLanguageModel
from tokenizer import load_text, build_tokenizer
from memory_manager import (
    load_project_notes,
    load_observations,
    save_observation,
    load_permanent_memory,
    save_memory,
)

from tools import (
    inspect_project_file,
    show_help, 
    show_notes, 
    show_status, 
    show_memory, 
    search_memory,
    show_permanent_memory,
    read_file,
    search_files,
    inspect_project_file,
)

from retrieval import retrieve_memory


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

conversation_history = []
max_history_items = 6

while True:
    prompt = input("You: ")
    relevant_memory = retrieve_memory(prompt)
    
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
    
    if prompt.lower().startswith("/search "):
        query = prompt[8:].strip()
        print(search_memory(query))
        continue
    
    if prompt.lower() == "/history":
        if conversation_history:
            print("\n".join(conversation_history))
        else:
            print("No conversation history yet.")
        continue
    
    if prompt.lower().startswith("/remember "):
        memory_item = prompt[10:].strip()
        print(save_memory(memory_item))
        continue

    if prompt.lower() == "/recall":
        print(show_permanent_memory())
        continue
    
    if prompt.lower().startswith("/observe "):
        observation = prompt[9:].strip()
        print(save_observation(observation))
        observations = load_observations()
        continue
    
    if prompt.lower().startswith("/read "):
        file_path = prompt[6:].strip()
        print(read_file(file_path))
        continue
    
    if prompt.lower().startswith("/searchfiles "):
        query = prompt[13:].strip()

        print(
            search_files(query)
        )

        continue
    
    if prompt.lower().startswith("/inspect "):
        query = prompt[9:].strip()
        print(inspect_project_file(query))
        continue
    
    
    recent_history = "\n".join(conversation_history[-max_history_items:])

    full_prompt = f"""
    Relevant Memory:
    {relevant_memory}

    Conversation:
    {recent_history}

    User:
    {prompt}

    MARPA:
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
    
    stop_patterns = [
        "User:", 
        "\n\n\n",
    ]

    for pattern in stop_patterns:
        if pattern in output:
            output = output.split(pattern)[0].strip()
            
    if not output:
        output = "I am still forming a response."

    print("\nMARPA:")
    print(output)
    print()
    
    conversation_history.append(f"User: {prompt}")
    conversation_history.append(f"MARPA: {output}")
    
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]
