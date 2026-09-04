from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from pydantic import BaseModel

from config import CONFIG
from web_client import reset_conversation, stream_prompt
from profile_manager import (
    create_profile,
    list_profiles,
)

app = FastAPI(
    title="MARPA Web",
    description="Browser interface for the MARPA daemon.",
    version="0.1.0",
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = PROJECT_ROOT / "web" / "index.html"
WEB_DIR = PROJECT_ROOT / "web"


class ConversationResetRequest(BaseModel):
    user_id: str = "kevyn"


class ProfileCreateRequest(BaseModel):
    display_name: str


class ChatRequest(BaseModel):
    prompt: str
    user_id: str = "kevyn"


@app.get("/config")
def runtime_config() -> dict[str, str]:
    """Return non-sensitive MARPA runtime information."""

    return {
        "node_name": CONFIG["marpa"]["node_name"],
        "installation_mode": CONFIG["marpa"]["installation_mode"],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "marpa-web",
    }


@app.get("/profiles")
def profiles() -> list[dict[str, str]]:
    return list_profiles()


@app.post("/profiles")
def create_user_profile(
    request: ProfileCreateRequest,
) -> dict[str, str]:
    try:
        return create_profile(
            request.display_name
        )

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to create profile.",
        ) from error


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    if not INDEX_FILE.exists():
        return HTMLResponse(
            """
            <!doctype html>
            <html lang="en">
                <head>
                    <meta charset="utf-8">
                    <title>MARPA</title>
                </head>
                <body>
                    <h1>MARPA Web</h1>
                    <p>The web server is running.</p>
                    <p>The chat interface has not been added yet.</p>
                </body>
            </html>
            """
        )

    return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))

@app.get("/app.js")
def javascript():
    return FileResponse(WEB_DIR / "app.js")


@app.post("/chat")
def chat(request: ChatRequest) -> StreamingResponse:
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="A non-empty prompt is required.",
        )

    return StreamingResponse(
        stream_prompt(
            prompt,
            user_id=request.user_id,
        ),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
    )


@app.post("/conversation/reset")
def reset_active_conversation(
    request: ConversationResetRequest,
) -> dict[str, str]:
    try:
        reset_conversation(
            user_id=request.user_id,
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    return {
        "status": "ok",
        "message": "Conversation reset.",
    }
