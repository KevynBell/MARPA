import json
import socketserver
import threading
from collections.abc import Callable

from agent_router import route_prompt
from llm_backend import ask_local_model
from memory_manager import save_conversation_exchange


HOST = "127.0.0.1"
PORT = 5050
MAX_HISTORY_ITEMS = 10


class MARPAEngine:
    """Long-running MARPA conversation engine."""

    def __init__(self) -> None:
        self.conversation_history: list[str] = []
        self.lock = threading.Lock()

    def _remember_exchange(self, prompt: str, response: str) -> None:
        self.conversation_history.append(f"User: {prompt}")
        self.conversation_history.append(f"MARPA: {response}")

        if len(self.conversation_history) > MAX_HISTORY_ITEMS:
            self.conversation_history = self.conversation_history[
                -MAX_HISTORY_ITEMS:
            ]

        save_conversation_exchange(prompt, response)

    def _build_prompt(self, prompt: str) -> str:
        conversation_context = "\n".join(
            self.conversation_history[-4:]
        )

        return f"""You are MARPA, Kevyn's local AI assistant.
Help with software development, debugging, planning, documentation, and learning.
Answer the user's current request directly and concisely.

Recent session:
{conversation_context}

User: {prompt}
MARPA:"""

    def respond(
        self,
        prompt: str,
        on_chunk: Callable[[str], None],
    ) -> str:
        """
        Process one request.

        A lock prevents multiple model requests from competing for the
        machine's limited CPU and memory at the same time.
        """
        with self.lock:
            routed_response = route_prompt(prompt)

            if routed_response is not None:
                on_chunk(routed_response)
                self._remember_exchange(prompt, routed_response)
                return routed_response

            model_prompt = self._build_prompt(prompt)

            response = ask_local_model(
                model_prompt,
                on_chunk=on_chunk,
                show_debug=False,
            )

            self._remember_exchange(prompt, response)
            return response


ENGINE = MARPAEngine()


class MARPARequestHandler(socketserver.StreamRequestHandler):
    """Handle one newline-delimited JSON request."""

    def send_message(self, message: dict) -> None:
        encoded = json.dumps(message).encode("utf-8") + b"\n"
        self.wfile.write(encoded)
        self.wfile.flush()

    def handle(self) -> None:
        client_address = self.client_address[0]
        print(f"[MARPA server] Connection from {client_address}")

        raw_request = self.rfile.readline()

        if not raw_request:
            return

        try:
            request = json.loads(raw_request.decode("utf-8"))
            prompt = str(request.get("prompt", "")).strip()

            if not prompt:
                self.send_message(
                    {
                        "type": "error",
                        "message": "A non-empty prompt is required.",
                    }
                )
                return

            def send_chunk(chunk: str) -> None:
                self.send_message(
                    {
                        "type": "chunk",
                        "text": chunk,
                    }
                )

            response = ENGINE.respond(prompt, send_chunk)

            self.send_message(
                {
                    "type": "done",
                    "response": response,
                }
            )

            print(
                f"[MARPA server] Completed request from {client_address}"
            )

        except BrokenPipeError:
            print(
                f"[MARPA server] Client {client_address} disconnected"
            )

        except Exception as error:
            print(f"[MARPA server] Request error: {error}")

            try:
                self.send_message(
                    {
                        "type": "error",
                        "message": str(error),
                    }
                )
            except Exception:
                pass


class MARPAServer(socketserver.TCPServer):
    allow_reuse_address = True


def main() -> None:
    print(f"[MARPA server] Listening on {HOST}:{PORT}")

    with MARPAServer((HOST, PORT), MARPARequestHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
