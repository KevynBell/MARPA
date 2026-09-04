import json
import socketserver
import threading
from collections.abc import Callable

from config import CONFIG
from agent_router import route_prompt
from llm_backend import ask_local_model
from memory_manager import (
    DEFAULT_USER_ID,
    load_permanent_memory,
    load_recent_conversation,
    sanitize_user_id,
    save_conversation_exchange,
)


HOST = CONFIG["daemon"]["host"]
PORT = CONFIG["daemon"]["port"]
MAX_HISTORY_ITEMS = 10


class MARPAEngine:
    """Long-running MARPA conversation engine."""

    def __init__(self) -> None:
        self.conversation_histories: dict[str, list[str]] = {}
        self.fresh_conversations: set[str] = set()
        self.lock = threading.Lock()

    def _remember_exchange(
        self,
        user_id: str,
        prompt: str,
        response: str,
    ) -> None:
        history = self.conversation_histories.setdefault(
            user_id,
            [],
        )

        history.append(f"User: {prompt}")
        history.append(f"MARPA: {response}")

        if len(history) > MAX_HISTORY_ITEMS:
            self.conversation_histories[user_id] = history[
                -MAX_HISTORY_ITEMS:
            ]

        save_conversation_exchange(
            prompt,
            response,
            user_id=user_id,
        )

        self.fresh_conversations.discard(user_id)

    def reset_conversation(
        self,
        user_id: str,
    ) -> None:
        """Start a fresh active conversation without deleting saved history."""

        self.conversation_histories[user_id] = []
        self.fresh_conversations.add(user_id)

    def _build_prompt(
        self,
        user_id: str,
        prompt: str,
    ) -> str:
        history = self.conversation_histories.setdefault(
            user_id,
            [],
        )

        if history:
            conversation_context = "\n".join(history[-4:])

        elif user_id in self.fresh_conversations:
            conversation_context = ""

        else:
            conversation_context = load_recent_conversation(
                limit=4,
                user_id=user_id,
            )

        permanent_memory = load_permanent_memory(
            user_id=user_id,
        )

        return f"""You are MARPA, a local AI assistant.
Help with software development, debugging, planning, documentation, and learning.
Answer the user's current request directly and concisely.

Response Formatting:
- Use valid GitHub-Flavored Markdown when formatting improves readability.
- Use headings, lists, bold text, inline code, and fenced code blocks appropriately.
- Only place source code or literal technical output inside fenced code blocks.
- Always close every fenced code block you open.
- Never wrap ordinary prose, headings, or lists inside a code fence.
- Keep formatting proportional to the complexity of the response.

Conversation Rules:
- Treat statements made by the current user in Recent Conversation as authoritative context.
- Use prior user messages to resolve follow-up questions and references.
- Previous MARPA responses are historical context and may contain mistakes.
- If a prior MARPA response conflicts with an explicit user statement, trust the user's statement.
- Do not claim information is unknown when it is explicitly present in Recent Conversation or Permanent Memory.

User ID:
{user_id}

Permanent Memory:
{permanent_memory}

Recent Conversation:
{conversation_context}

User: {prompt}
MARPA:"""

    def respond(
        self,
        user_id: str,
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

                self._remember_exchange(
                    user_id,
                    prompt,
                    routed_response,
                )

                return routed_response

            model_prompt = self._build_prompt(
                user_id,
                prompt,
            )

            response = ask_local_model(
                model_prompt,
                on_chunk=on_chunk,
                show_debug=False,
            )

            self._remember_exchange(
                user_id,
                prompt,
                response,
            )

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

            user_id = sanitize_user_id(
                str(
                    request.get(
                        "user_id",
                        DEFAULT_USER_ID,
                    )
                )
            )

            request_type = str(
                request.get(
                    "type",
                    "prompt",
                )
            )

            if request_type == "reset_conversation":
                ENGINE.reset_conversation(user_id)

                self.send_message(
                    {
                        "type": "done",
                        "message": "Conversation reset.",
                    }
                )

                print(
                    f"[MARPA server] Reset conversation for {user_id}"
                )

                return

            prompt = str(
                request.get(
                    "prompt",
                    "",
                )
            ).strip()

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

            response = ENGINE.respond(
                user_id,
                prompt,
                send_chunk,
            )

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
