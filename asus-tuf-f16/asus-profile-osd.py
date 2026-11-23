#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import subprocess
import sys

# Path to platform profile state
PROFILE_FILE = Path("/sys/firmware/acpi/platform_profile")

# Profile matching patterns and corresponding KDE OSD (icon, label)
PROFILE_DETAILS = {
    "performance": ("battery-profile-performance", "Performance"),
    "quiet": ("battery-profile-powersave", "Quiet"),
    "silent": ("battery-profile-powersave", "Quiet"),
    "low-power": ("battery-profile-powersave", "Quiet"),
    "balanced": ("battery-profile-balanced", "Balanced"),
}

# Default fallback OSD details
DEFAULT_DETAILS = ("battery-profile-balanced", "Balanced")


def get_current_profile(path: Path) -> str:
    """Read and normalize the current ACPI platform profile."""
    profile = path.read_text().strip().lower()
    return "".join(profile.split())


def get_profile_details(profile: str) -> tuple[str, str]:
    """Determine the appropriate KDE icon and label."""
    for pattern, details in PROFILE_DETAILS.items():
        if pattern in profile:
            return details

    return DEFAULT_DETAILS


def get_active_user() -> str | None:
    """Detect the first logged-in graphical user."""
    result = subprocess.run(
        ["loginctl", "list-users", "--no-legend"],
        capture_output=True,
        text=True,
        check=True,
    )

    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 2:
            return fields[1]

    return None


def show_osd(icon: str, label: str, username: str) -> None:
    """Display the power profile notification in KDE Plasma."""
    uid = subprocess.run(
        ["id", "-u", username],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    runtime_dir = f"/run/user/{uid}"

    env = os.environ.copy()
    env["XDG_RUNTIME_DIR"] = runtime_dir
    env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={runtime_dir}/bus"

    subprocess.run(
        [
            "runuser",
            "-u",
            username,
            "--",
            "qdbus6",
            "org.kde.plasmashell",
            "/org/kde/osdService",
            "org.kde.osdService.showText",
            icon,
            f"Power Profile: {label}",
        ],
        env=env,
        check=True,
    )


def main() -> None:
    # Check required files and system commands
    required_cmds = ("loginctl", "id", "runuser", "qdbus6")
    if not PROFILE_FILE.is_file() or not all(shutil.which(cmd) for cmd in required_cmds):
        print("Error: Required system files or commands not found.", file=sys.stderr)
        sys.exit(1)

    try:
        # Read current platform profile
        profile = get_current_profile(PROFILE_FILE)
        icon, label = get_profile_details(profile)

        # Find active user session
        username = get_active_user()
        if not username:
            print("Warning: No logged-in user detected.", file=sys.stderr)
            return

        # Display KDE OSD notification
        show_osd(icon, label, username)

    except PermissionError:
        print(
            "Error: Permission denied. Run this script as root.",
            file=sys.stderr,
        )
        sys.exit(1)

    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Error displaying KDE OSD: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()