import json
import time
import urllib.request
from collections.abc import Callable

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"
MODEL_NAME = "qwen2.5:3b"

OutputHandler = Callable[[str], None]


def seconds_from_ns(value: int | float | None) -> float:
    """Convert Ollama nanoseconds to seconds."""
    return value / 1_000_000_000 if value else 0.0


def terminal_output(text: str) -> None:
    """Write a streamed model chunk to the current terminal."""
    print(text, end="", flush=True)


def ask_local_model(
    prompt: str,
    on_chunk: OutputHandler | None = None,
    show_debug: bool = True,
) -> str:
    """
    Send a prompt to Ollama and return the completed response.

    When on_chunk is provided, each generated text chunk is passed to it.
    Otherwise, chunks are printed directly to the terminal.
    """
    output_handler = on_chunk or terminal_output
    estimated_tokens = len(prompt) // 4

    if show_debug:
        print(
            f"[MARPA debug] Prompt size: {len(prompt):,} characters "
            f"(roughly {estimated_tokens:,} tokens)"
        )
        print("\nMARPA:")

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

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.perf_counter()
    first_token_time = None
    output_parts: list[str] = []
    final_result: dict = {}

    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            for raw_line in response:
                if not raw_line.strip():
                    continue

                result = json.loads(raw_line.decode("utf-8"))
                chunk = result.get("response", "")

                if chunk:
                    if first_token_time is None:
                        first_token_time = time.perf_counter() - started

                    output_handler(chunk)
                    output_parts.append(chunk)

                if result.get("done"):
                    final_result = result

        wall_time = time.perf_counter() - started
        load_time = seconds_from_ns(final_result.get("load_duration"))
        prompt_time = seconds_from_ns(
            final_result.get("prompt_eval_duration")
        )
        generation_time = seconds_from_ns(
            final_result.get("eval_duration")
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

        if show_debug:
            print()
            print(
                "[MARPA performance] "
                f"first_token={first_token_display} | "
                f"total={wall_time:.2f}s | "
                f"load={load_time:.2f}s | "
                f"prompt={prompt_time:.2f}s "
                f"({prompt_tokens} tokens) | "
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

        if show_debug:
            print(message)

        return message
