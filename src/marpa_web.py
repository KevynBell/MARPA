from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from web_client import send_prompt


app = FastAPI(
    title="MARPA Web",
    description="Browser interface for the MARPA daemon.",
    version="0.1.0",
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = PROJECT_ROOT / "web" / "index.html"


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "marpa-web",
    }


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


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="A non-empty prompt is required.",
        )

    try:
        response = send_prompt(prompt)
    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    return ChatResponse(response=response)
