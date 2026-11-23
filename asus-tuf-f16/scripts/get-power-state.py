#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import sys

# Intel RAPL CPU package power limit files
CPU_POWER_FILES = (
    (
        "PL1 (Sustained Power)",
        Path("/sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw"),
    ),
    (
        "PL2 (Short Burst Power)",
        Path("/sys/class/powercap/intel-rapl/intel-rapl:0/constraint_1_power_limit_uw"),
    ),
)

# Convert microwatts to watts
DIVISOR = 1_000_000

# PCI bus address for the NVIDIA GPU
PCI_BUS_ID = "0000:01:00.0"

# GPU driver and PCI runtime power status files
GPU_STATUS_FILES = (
    Path(f"/proc/driver/nvidia/gpus/{PCI_BUS_ID}/power"),
    Path(f"/sys/bus/pci/devices/{PCI_BUS_ID}/power/control"),
    Path(f"/sys/bus/pci/devices/{PCI_BUS_ID}/power/runtime_status"),
)

# Commands to query NVIDIA GPU status
NVIDIA_COMMANDS = (
    ["nvidia-smi", "-q", "-d", "POWER"],
    ["nvidia-smi"],
)


def print_cpu_power_limit(label: str, path: Path) -> None:
    """Read and print an Intel RAPL power limit in microwatts and watts."""
    print(f"=== {label}: {path} ===")
    if not path.is_file():
        print("File not found.\n", file=sys.stderr)
        return

    try:
        raw_value = path.read_text().strip()
    except (OSError, PermissionError) as error:
        print(f"Error reading file: {error}\n", file=sys.stderr)
        return

    try:
        microwatts = int(raw_value)
        watts = microwatts / DIVISOR
        print(f"{microwatts} uW ({watts:g} W)\n")
    except ValueError:
        print(f"{raw_value}\n")


def print_file_contents(path: Path) -> None:
    """Read and print the contents of a system file if it exists."""
    print(f"=== {path} ===")
    if not path.is_file():
        print("File not found.\n", file=sys.stderr)
        return

    try:
        content = path.read_text().strip()
        print(f"{content}\n")
    except (OSError, PermissionError) as error:
        print(f"Error reading file: {error}\n", file=sys.stderr)


def run_command(cmd: list[str]) -> None:
    """Execute a system command and print its output."""
    print(f"=== {' '.join(cmd)} ===")
    if not shutil.which(cmd[0]):
        print(f"Command '{cmd[0]}' not found.\n", file=sys.stderr)
        return

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout.strip())
        print()
    except subprocess.CalledProcessError as error:
        print(f"Command failed: {error}", file=sys.stderr)
        if error.stderr:
            print(error.stderr.strip(), file=sys.stderr)
        print()


def main() -> None:
    # Check Intel RAPL PL1 and PL2 limits first
    for label, file_path in CPU_POWER_FILES:
        print_cpu_power_limit(label, file_path)

    # Print GPU driver and PCI runtime power states
    for file_path in GPU_STATUS_FILES:
        print_file_contents(file_path)

    # Query NVIDIA SMI power and general status
    for command in NVIDIA_COMMANDS:
        run_command(command)


if __name__ == "__main__":
    main()