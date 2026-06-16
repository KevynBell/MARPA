import json
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"


def ask_local_model(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "").strip()

    except Exception as error:
        return f"Local model error: {error}"