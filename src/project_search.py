from pathlib import Path

PROJECT_ROOT = Path.cwd()

SEARCH_EXTENSIONS = {
    ".py",
    ".txt",
    ".md"
}

EXCLUDED_DIRS = {
    ".venv",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "site-packages",
}


def is_excluded(file_path):
    return any(
        part in EXCLUDED_DIRS
        for part in file_path.parts
    )


def search_project_files(query):
    matches = []

    for file in PROJECT_ROOT.rglob("*"):

        if is_excluded(file):
            continue

        if file.suffix not in SEARCH_EXTENSIONS:
            continue

        try:
            text = file.read_text(
                encoding="utf-8"
            )

            if query.lower() in text.lower():
                matches.append(
                    str(
                        file.relative_to(
                            PROJECT_ROOT
                        )
                    )
                )

        except UnicodeDecodeError:
            continue
        except PermissionError:
            continue

    if not matches:
        return "No matching files found."

    return "\n".join(matches[:15])