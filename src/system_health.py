import subprocess
import json
import urllib.error
import urllib.request

from llm_backend import (
    MODEL_NAME,
    OLLAMA_BASE_URL,
)

MARPA_SERVICES = {
    "marpa": "marpa.service",
    "web": "marpa-web.service",
    "tailscale": "tailscaled.service",
}


def get_service_status(
    service_name: str,
) -> str:
    """Return the current systemd state for a service."""

    result = subprocess.run(
        [
            "systemctl",
            "is-active",
            service_name,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    status = result.stdout.strip()

    if status:
        return status

    return "unknown"


def get_core_service_health() -> dict[str, str]:
    """Return health states for MARPA's core system services."""

    return {
        name: get_service_status(service)
        for name, service in MARPA_SERVICES.items()
    }


def is_service_healthy(status: str) -> bool:
    """Return whether a systemd service state is considered healthy."""

    return status == "active"


def get_core_service_summary() -> dict[str, dict[str, object]]:
    """Return raw and interpreted health for MARPA's core services."""

    service_states = get_core_service_health()

    return {
        name: {
            "status": status,
            "healthy": is_service_healthy(status),
        }
        for name, status in service_states.items()
    }


def get_ollama_health() -> dict[str, object]:
    """Return Ollama availability and configured model status."""

    url = f"{OLLAMA_BASE_URL}/api/tags"

    try:
        with urllib.request.urlopen(
            url,
            timeout=5,
        ) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )

    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
    ) as error:
        return {
            "available": False,
            "model_available": False,
            "model": MODEL_NAME,
            "error": str(error),
        }

    models = payload.get("models", [])

    model_names = {
        str(model.get("name", ""))
        for model in models
    }

    return {
        "available": True,
        "model_available": MODEL_NAME in model_names,
        "model": MODEL_NAME,
        "error": None,
    }


def get_system_health() -> dict[str, object]:
    """Return a combined health snapshot for MARPA."""

    services = get_core_service_summary()
    ollama = get_ollama_health()

    services_healthy = all(
        service["healthy"]
        for service in services.values()
    )

    ollama_healthy = (
        ollama["available"]
        and ollama["model_available"]
    )

    return {
        "healthy": services_healthy and ollama_healthy,
        "services": services,
        "ollama": ollama,
    }


def format_system_health(
    health: dict[str, object],
) -> str:
    """Format MARPA health information for a human-readable response."""

    overall = (
        "Everything looks healthy."
        if health["healthy"]
        else "MARPA detected one or more problems."
    )

    services = health["services"]
    ollama = health["ollama"]

    def service_label(name: str) -> str:
        labels = {
            "marpa": "MARPA",
            "web": "Web interface",
            "tailscale": "Tailscale",
        }

        return labels.get(name, name.title())

    lines = [overall, ""]

    for name, service in services.items():
        status = "Online" if service["healthy"] else "Offline"

        lines.append(
            f"- **{service_label(name)}:** {status}"
        )

    local_ai_status = (
        "Online"
        if ollama["available"]
        else "Offline"
    )

    model_status = (
        "Available"
        if ollama["model_available"]
        else "Unavailable"
    )

    lines.extend(
        [
            f"- **Local AI:** {local_ai_status}",
            f"- **Model:** {ollama['model']} ({model_status})",
        ]
    )

    return "\n".join(lines)
