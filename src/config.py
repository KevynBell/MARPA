from pathlib import Path
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "marpa.toml"


def load_config() -> dict:
    """Load MARPA's installation configuration."""

    with CONFIG_PATH.open("rb") as config_file:
        return tomllib.load(config_file)


CONFIG = load_config()
