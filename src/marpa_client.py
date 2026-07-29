import json
import socket


HOST = "127.0.0.1"
PORT = 5050


def send_prompt(prompt: str) -> None:
    request = json.dumps({"prompt": prompt}).encode("utf-8") + b"\n"

    try:
        with socket.create_connection((HOST, PORT), timeout=10) as connection:
            connection.sendall(request)

            print("\nMARPA:")

            with connection.makefile("r", encoding="utf-8") as response:
                for line in response:
                    message = json.loads(line)
                    message_type = message.get("type")

                    if message_type == "chunk":
                        print(
                            message.get("text", ""),
                            end="",
                            flush=True,
                        )

                    elif message_type == "done":
                        print()
                        return

                    elif message_type == "error":
                        print(
                            f"\nMARPA server error: "
                            f"{message.get('message', 'Unknown error')}"
                        )
                        return

    except ConnectionRefusedError:
        print(
            "MARPA is not running. Start src/marpa_server.py "
            "or check the systemd service."
        )

    except OSError as error:
        print(f"Unable to contact MARPA: {error}")


def main() -> None:
    print("MARPA client connected mode.")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            prompt = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if prompt.lower() in {"quit", "exit", "/quit"}:
            break

        if not prompt:
            continue

        send_prompt(prompt)
        print()


if __name__ == "__main__":
    main()
