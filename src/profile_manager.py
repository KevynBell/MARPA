import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
USERS_DIR = PROJECT_ROOT / "memory" / "users"


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
