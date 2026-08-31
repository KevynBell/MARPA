import os
import platform
import shutil
import socket
import time
from pathlib import Path


OS_RELEASE_PATH = Path("/etc/os-release")
PROC_UPTIME_PATH = Path("/proc/uptime")
MEMINFO_PATH = Path("/proc/meminfo")


def get_os_name() -> str:
    """Return the operating system's human-readable name."""

    if OS_RELEASE_PATH.exists():
        for line in OS_RELEASE_PATH.read_text(
            encoding="utf-8"
        ).splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip('"')

    return platform.system()


def get_uptime_seconds() -> int:
    """Return system uptime in whole seconds."""

    if PROC_UPTIME_PATH.exists():
        uptime_text = PROC_UPTIME_PATH.read_text(
            encoding="utf-8"
        ).split()[0]

        return int(float(uptime_text))

    return int(time.monotonic())


def format_duration(seconds: int) -> str:
    """Convert seconds into a human-readable duration."""

    if seconds < 60:
        return (
            f"{seconds} second"
            if seconds == 1
            else f"{seconds} seconds"
        )

    minutes, remaining_seconds = divmod(seconds, 60)

    if minutes < 60:
        parts = [
            f"{minutes} minute"
            if minutes == 1
            else f"{minutes} minutes"
        ]

        if remaining_seconds:
            parts.append(
                f"{remaining_seconds} second"
                if remaining_seconds == 1
                else f"{remaining_seconds} seconds"
            )

        return ", ".join(parts)

    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = []

    if days:
        parts.append(
            f"{days} day"
            if days == 1
            else f"{days} days"
        )

    if hours:
        parts.append(
            f"{hours} hour"
            if hours == 1
            else f"{hours} hours"
        )

    if minutes:
        parts.append(
            f"{minutes} minute"
            if minutes == 1
            else f"{minutes} minutes"
        )

    return ", ".join(parts)


def format_bytes(byte_count: int) -> str:
    """Convert a byte count into a human-readable size."""

    units = ("B", "KB", "MB", "GB", "TB", "PB")
    size = float(byte_count)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"

            return f"{size:.1f} {unit}"

        size /= 1024

    return f"{byte_count} B"


def get_memory_info() -> dict[str, int]:
    """Return total and available system memory in bytes."""

    memory_values = {}

    if not MEMINFO_PATH.exists():
        return {
            "total_bytes": 0,
            "available_bytes": 0,
        }

    for line in MEMINFO_PATH.read_text(
        encoding="utf-8"
    ).splitlines():
        key, value = line.split(":", 1)

        if key in {"MemTotal", "MemAvailable"}:
            kilobytes = int(value.strip().split()[0])
            memory_values[key] = kilobytes * 1024

    return {
        "total_bytes": memory_values.get("MemTotal", 0),
        "available_bytes": memory_values.get("MemAvailable", 0),
    }


def get_system_info() -> dict[str, object]:
    """Return a read-only snapshot of the local MARPA host."""

    disk = shutil.disk_usage("/")
    memory = get_memory_info()

    return {
        "hostname": socket.gethostname(),
        "os": get_os_name(),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "cpu_count": os.cpu_count(),
        "uptime_seconds": get_uptime_seconds(),
        "disk_total_bytes": disk.total,
        "disk_used_bytes": disk.used,
        "disk_free_bytes": disk.free,
        "memory_total_bytes": memory["total_bytes"],
        "memory_available_bytes": memory["available_bytes"],
    }


def format_system_summary(
    info: dict[str, object],
) -> str:
    """Format system information for a human-readable response."""

    return (
        f"MARPA is running on **{info['hostname']}**.\n\n"
        f"- **System:** {info['os']}\n"
        f"- **Kernel:** {info['kernel']}\n"
        f"- **Architecture:** {info['architecture']}\n"
        f"- **CPU:** {info['cpu_count']} cores\n"
        f"- **Memory:** "
        f"{format_bytes(info['memory_available_bytes'])} available / "
        f"{format_bytes(info['memory_total_bytes'])} total\n"
        f"- **Storage:** "
        f"{format_bytes(info['disk_free_bytes'])} free / "
        f"{format_bytes(info['disk_total_bytes'])} total\n"
        f"- **Uptime:** {format_duration(info['uptime_seconds'])}"
    )
