import json
import socket
from collections.abc import Iterator

HOST = "127.0.0.1"
PORT = 5050
DEFAULT_USER_ID = "kevyn"


def stream_prompt(
    prompt: str,
    user_id: str = DEFAULT_USER_ID,
) -> Iterator[str]:
    """Send a prompt to MARPA and yield response chunks as they arrive."""

    request = json.dumps(
        {
            "user_id": user_id,
            "prompt": prompt,
        }
    ).encode("utf-8") + b"\n"

    try:
        with socket.create_connection((HOST, PORT), timeout=10) as connection:
            connection.settimeout(None)
            connection.sendall(request)

            with connection.makefile("r", encoding="utf-8") as response:
                for line in response:
                    message = json.loads(line)
                    message_type = message.get("type")

                    if message_type == "chunk":
                        yield message.get("text", "")

                    elif message_type == "done":
                        return

                    elif message_type == "error":
                        raise RuntimeError(
                            message.get("message", "Unknown MARPA error")
                        )

    except ConnectionRefusedError as error:
        raise RuntimeError(
            "Unable to connect to the MARPA daemon."
        ) from error

    except OSError as error:
        raise RuntimeError(str(error)) from error


def send_prompt(
    prompt: str,
    user_id: str = DEFAULT_USER_ID,
) -> str:
    """Send a prompt to MARPA and return the completed response."""

    return "".join(
        stream_prompt(
            prompt,
            user_id=user_id,
        )
    )

def reset_conversation(
    user_id: str = DEFAULT_USER_ID,
) -> None:
    """Reset MARPA's active conversation context for one user."""

    request = json.dumps(
        {
            "type": "reset_conversation",
            "user_id": user_id,
        }
    ).encode("utf-8") + b"\n"

    try:
        with socket.create_connection((HOST, PORT), timeout=10) as connection:
            connection.sendall(request)

            with connection.makefile("r", encoding="utf-8") as response:
                for line in response:
                    message = json.loads(line)
                    message_type = message.get("type")

                    if message_type == "done":
                        return

                    if message_type == "error":
                        raise RuntimeError(
                            message.get(
                                "message",
                                "Unknown MARPA error",
                            )
                        )

    except ConnectionRefusedError as error:
        raise RuntimeError(
            "Unable to connect to the MARPA daemon."
        ) from error

    except OSError as error:
        raise RuntimeError(str(error)) from error
