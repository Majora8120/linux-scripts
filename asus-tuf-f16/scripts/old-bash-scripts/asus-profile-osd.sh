#!/bin/bash
# --- KDE Plasma OSD Integration ---

# Read, remove all whitespace/newlines, and convert to lowercase
CURRENT_PROFILE=$(cat /sys/firmware/acpi/platform_profile 2>/dev/null | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')

# Use wildcard patterns (*...*) to safely match variations
case "$CURRENT_PROFILE" in
    *performance*)
        ICON="battery-profile-performance"
        LABEL="Performance"
        ;;
    *quiet*|*silent*|*low-power*)
        ICON="battery-profile-powersave"
        LABEL="Quiet"
        ;;
    *)
        ICON="battery-profile-balanced"
        LABEL="Balanced"
        ;;
esac

# Detect the active graphical user and UID dynamically
TARGET_USER=$(loginctl list-users --no-legend | awk '{print $2}' | head -n1)
if [ -n "$TARGET_USER" ]; then
    TARGET_UID=$(id -u "$TARGET_USER")

    export XDG_RUNTIME_DIR="/run/user/$TARGET_UID"
    export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"

    # Push the OSD text into the user's Wayland session via runuser
    runuser -u "$TARGET_USER" -- qdbus6 org.kde.plasmashell /org/kde/osdService org.kde.osdService.showText "$ICON" "Power Profile: $LABEL"
fi
