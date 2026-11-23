#!/usr/bin/env python3
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

# Display configuration
OUTPUT_NAME = "eDP-1"
TARGET_RESOLUTION = "1920x1200"
TARGET_REFRESH_RATE = 60

# ASUS panel overdrive state (1 = enabled, 0 = disabled)
PANEL_OVERDRIVE = 0

# Color-power tradeoff sequence to force DisplayPort renegotiation
COLOR_TRADEOFFS = (
    "prefer-efficiency",
    "prefer-accuracy",
)

# Regex to strip ANSI color escape sequences
ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


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


def get_user_session_command(cmd: list[str]) -> tuple[list[str], dict[str, str]]:
    """Wrap command with runuser and Wayland environment variables if running as root."""
    env = os.environ.copy()
    if os.geteuid() != 0:
        return cmd, env

    username = get_active_user()
    if not username:
        raise RuntimeError("No active graphical user session found.")

    uid = subprocess.run(
        ["id", "-u", username],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    runtime_dir = Path(f"/run/user/{uid}")
    sockets = sorted(runtime_dir.glob("wayland-*"))
    wayland_display = next(
        (s.name for s in sockets if not s.name.endswith(".lock")),
        "wayland-0",
    )

    env["XDG_RUNTIME_DIR"] = str(runtime_dir)
    env["WAYLAND_DISPLAY"] = wayland_display
    env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={runtime_dir}/bus"

    return ["runuser", "-u", username, "--", *cmd], env


def get_current_refresh_rate(output_name: str, resolution: str) -> int | None:
    """Query kscreen-doctor for the active refresh rate."""
    cmd, env = get_user_session_command(["kscreen-doctor", "-o"])
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )

    clean_output = ANSI_ESCAPE.sub("", result.stdout)
    mode_pattern = re.compile(rf"\b{re.escape(resolution)}@(\d+)(?:\.\d+)?\*")
    in_target_output = False

    for line in clean_output.splitlines():
        if "Output:" in line and output_name in line:
            in_target_output = True
            continue

        if in_target_output:
            if line.startswith("Output:"):
                break

            match = mode_pattern.search(line)
            if match:
                return int(match.group(1))

    return None


def set_display_mode(output_name: str, resolution: str, refresh_rate: int) -> None:
    """Set the display resolution and refresh rate."""
    mode = f"output.{output_name}.mode.{resolution}@{refresh_rate}"
    cmd, env = get_user_session_command(["kscreen-doctor", mode])
    subprocess.run(cmd, env=env, check=True)


def set_panel_overdrive(state: int) -> None:
    """Set the ASUS panel overdrive state."""
    subprocess.run(
        ["asusctl", "armoury", "set", "panel_overdrive", str(state)],
        check=True,
    )


def trigger_display_renegotiation(output_name: str) -> None:
    """Toggle color accuracy to force a DisplayPort renegotiation."""
    for tradeoff in COLOR_TRADEOFFS:
        cmd, env = get_user_session_command(
            ["kscreenctl", output_name, "set-color-power-tradeoff", tradeoff]
        )
        subprocess.run(cmd, env=env, check=True)


def main() -> None:
    # Check required commands
    required_cmds = ["kscreen-doctor", "kscreenctl", "asusctl"]
    if os.geteuid() == 0:
        required_cmds.extend(["loginctl", "id", "runuser"])

    if not all(shutil.which(cmd) for cmd in required_cmds):
        print("Error: Required system commands not found.", file=sys.stderr)
        sys.exit(1)

    try:
        # Read current refresh rate
        current_rate = get_current_refresh_rate(OUTPUT_NAME, TARGET_RESOLUTION)

        # Skip mode change if already at target refresh rate
        if current_rate == TARGET_REFRESH_RATE:
            print(f"Refresh rate is already {TARGET_REFRESH_RATE}Hz. Skipping.")
        else:
            set_display_mode(OUTPUT_NAME, TARGET_RESOLUTION, TARGET_REFRESH_RATE)

        # Disable panel overdrive
        set_panel_overdrive(PANEL_OVERDRIVE)

        # Force display refresh to prevent sluggish 60Hz behavior
        trigger_display_renegotiation(OUTPUT_NAME)

    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Error configuring display: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()