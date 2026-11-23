#!/usr/bin/env python3
from pathlib import Path
import sys

# Path to platform profile state
PROFILE_FILE = Path("/sys/firmware/acpi/platform_profile")

# Intel RAPL CPU Package Limits
PL1_FILE = Path(
    "/sys/class/powercap/intel-rapl/intel-rapl:0/"
    "constraint_0_power_limit_uw"
)

PL2_FILE = Path(
    "/sys/class/powercap/intel-rapl/intel-rapl:0/"
    "constraint_1_power_limit_uw"
)

# Convert watts to microwatts
MULTIPLIER = 1_000_000

# Power limits (watts)
PROFILES = {
    "quiet": {
        "pl1": 20,
        "pl2": 30,
    },
    "balanced": {
        "pl1": 35,
        "pl2": 45,
    },
    "performance": {
        "pl1": 55,
        "pl2": 80,
    },
}


def write_power_limit(path: Path, watts: int) -> None:
    """Write a power limit in microwatts."""
    microwatts = watts * MULTIPLIER
    path.write_text(str(microwatts))


def main() -> None:
    # Check required files
    if not PROFILE_FILE.is_file() or not PL1_FILE.is_file() or not PL2_FILE.is_file():
        print("Error: Required system files not found.", file=sys.stderr)
        sys.exit(1)

    # Read current platform profile
    current_profile = PROFILE_FILE.read_text().strip()

    # Ignore unknown profiles
    if current_profile not in PROFILES:
        print("Warning: Unknown power profile.", file=sys.stderr)
        return

    limits = PROFILES[current_profile]

    try:
        # Set PL1
        write_power_limit(PL1_FILE, limits["pl1"])

        # Set PL2 if available
        if PL2_FILE.is_file():
            write_power_limit(PL2_FILE, limits["pl2"])

    except PermissionError:
        print(
            "Error: Permission denied. Run this script as root.",
            file=sys.stderr,
        )
        sys.exit(1)

    except OSError as error:
        print(f"Error setting power limits: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
