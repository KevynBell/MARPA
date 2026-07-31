from web_client import send_prompt



HOST = "127.0.0.1"
PORT = 5050


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

        try:
            response = send_prompt(prompt)
            print(f"\nMARPA:\n{response}\n")
        except RuntimeError as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()
