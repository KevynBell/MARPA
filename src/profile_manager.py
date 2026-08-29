import json
import re

from memory_manager import (
    USERS_DIR,
    sanitize_user_id,
)


def make_user_id(display_name: str) -> str:
    """Convert a display name into a valid MARPA user ID."""

    cleaned_name = display_name.strip()

    if not cleaned_name:
        raise ValueError(
            "Display name cannot be empty."
        )

    candidate = re.sub(
        r"[^a-z0-9]+",
        "-",
        cleaned_name.lower(),
    ).strip("-")

    if not candidate:
        raise ValueError(
            "Display name must contain letters or numbers."
        )

    return sanitize_user_id(candidate)


def create_profile(
    display_name: str,
) -> dict[str, str]:
    """Create a new MARPA user profile."""

    cleaned_name = display_name.strip()
    user_id = make_user_id(cleaned_name)

    user_dir = USERS_DIR / user_id
    profile_path = user_dir / "profile.json"

    if user_dir.exists():
        raise ValueError(
            f'Profile "{user_id}" already exists.'
        )

    profile = {
        "user_id": user_id,
        "display_name": cleaned_name,
    }

    try:
        user_dir.mkdir(
            parents=True,
            exist_ok=False,
        )

        profile_path.write_text(
            json.dumps(
                profile,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    except OSError:
        if user_dir.exists() and not profile_path.exists():
            try:
                user_dir.rmdir()
            except OSError:
                pass

        raise

    return profile


def list_profiles() -> list[dict[str, str]]:
    """Return valid MARPA user profiles from the local users directory."""

    profiles: list[dict[str, str]] = []

    if not USERS_DIR.exists():
        return profiles

    for user_dir in sorted(USERS_DIR.iterdir()):
        if not user_dir.is_dir():
            continue

        profile_path = user_dir / "profile.json"

        if not profile_path.exists():
            continue

        try:
            data = json.loads(
                profile_path.read_text(
                    encoding="utf-8"
                )
            )

            user_id = user_dir.name

            display_name = str(
                data.get(
                    "display_name",
                    ""
                )
            ).strip()

            stored_user_id = str(
                data.get(
                    "user_id",
                    ""
                )
            ).strip()

            if stored_user_id != user_id:
                continue

            if not user_id or not display_name:
                continue

            profiles.append(
                {
                    "user_id": user_id,
                    "display_name": display_name,
                }
            )

        except (
            json.JSONDecodeError,
            OSError,
        ):
            continue

    return profiles
