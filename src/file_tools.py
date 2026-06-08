from pathlib import Path

PROJECT_ROOT = Path.cwd()
MAX_FILE_CHARS = 4000


def read_project_file(file_path):
    requested_path = Path(file_path)

    full_path = (PROJECT_ROOT / requested_path).resolve()

    if not full_path.exists():
        return f"File not found: {file_path}"

    if not full_path.is_file():
        return f"Path is not a file: {file_path}"

    try:
        full_path.relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        return "Access denied. File must be inside the MARPA project folder."

    content = full_path.read_text(encoding="utf-8")

    if len(content) > MAX_FILE_CHARS:
        content = content[:MAX_FILE_CHARS]
        content += "\n\n[File truncated for display.]"

    return content