import json
import time
import urllib.request


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"


def seconds_from_ns(value):
    """Convert Ollama nanoseconds to seconds."""
    return value / 1_000_000_000 if value else 0.0


def ask_local_model(prompt):
    estimated_tokens = len(prompt) // 4

    print(
        f"[MARPA debug] Prompt size: {len(prompt):,} characters "
        f"(roughly {estimated_tokens:,} tokens)"
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
        "keep_alive": "30m",
        "options": {
            "num_predict": 96,
            "num_ctx": 1024,
            "temperature": 0.7,
        },
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.perf_counter()
    first_token_time = None
    output_parts = []
    final_result = {}

    try:
        print("\nMARPA:")

        with urllib.request.urlopen(request, timeout=600) as response:
            for raw_line in response:
                if not raw_line.strip():
                    continue

                result = json.loads(raw_line.decode("utf-8"))

                chunk = result.get("response", "")

                if chunk:
                    if first_token_time is None:
                        first_token_time = time.perf_counter() - started

                    print(chunk, end="", flush=True)
                    output_parts.append(chunk)

                if result.get("done"):
                    final_result = result

        print()

        wall_time = time.perf_counter() - started
        load_time = seconds_from_ns(final_result.get("load_duration", 0))
        prompt_time = seconds_from_ns(
            final_result.get("prompt_eval_duration", 0)
        )
        generation_time = seconds_from_ns(
            final_result.get("eval_duration", 0)
        )

        prompt_tokens = final_result.get("prompt_eval_count", 0)
        generated_tokens = final_result.get("eval_count", 0)

        tokens_per_second = (
            generated_tokens / generation_time
            if generation_time > 0
            else 0.0
        )

        first_token_display = (
            f"{first_token_time:.2f}s"
            if first_token_time is not None
            else "unknown"
        )

        print(
            "[MARPA performance] "
            f"first_token={first_token_display} | "
            f"total={wall_time:.2f}s | "
            f"load={load_time:.2f}s | "
            f"prompt={prompt_time:.2f}s ({prompt_tokens} tokens) | "
            f"generation={generation_time:.2f}s "
            f"({generated_tokens} tokens, "
            f"{tokens_per_second:.2f} tok/s)"
        )

        return "".join(output_parts).strip()

    except Exception as error:
        wall_time = time.perf_counter() - started
        message = (
            f"Local model error after {wall_time:.2f} seconds: {error}"
        )
        print(message)
        return message
