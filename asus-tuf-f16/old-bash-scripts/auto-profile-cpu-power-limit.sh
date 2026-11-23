#!/bin/bash

# Path to platform profile state
PROFILE_FILE="/sys/firmware/acpi/platform_profile"

# Intel RAPL CPU Package Limits
PL1_FILE="/sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw"
PL2_FILE="/sys/class/powercap/intel-rapl/intel-rapl:0/constraint_1_power_limit_uw"

# The multiplier for the power limits. Used to convert the limits, which are in watts, to microwatts.
MULTIPLIER=1000000

# Quiet: 20W PL1 / 30W PL2
QUIET_PL1=20
QUIET_PL2=30

# Balanced: 35W PL1 / 45W PL2 (Stops CPU spikes while maintaining speed)
BALANCED_PL1=35
BALANCED_PL2=45

# Performance: 55W PL1 / 80W PL2 (or whatever maximum limits you prefer)
PERFORMANCE_PL1=55
PERFORMANCE_PL2=80

if [ ! -f "$PROFILE_FILE" ] || [ ! -f "$PL1_FILE" ]; then
    exit 0
fi

CURRENT_PROFILE=$(cat "$PROFILE_FILE")

case "$CURRENT_PROFILE" in
    "quiet")
        echo $((QUIET_PL1 * MULTIPLIER)) > "$PL1_FILE"
        [ -f "$PL2_FILE" ] && echo $((QUIET_PL2 * MULTIPLIER)) > "$PL2_FILE"
        ;;
    "balanced")
        echo $((BALANCED_PL1 * MULTIPLIER)) > "$PL1_FILE"
        [ -f "$PL2_FILE" ] && echo $((BALANCED_PL2 * MULTIPLIER)) > "$PL2_FILE"
        ;;
    "performance")
        echo $((PERFORMANCE_PL1 * MULTIPLIER)) > "$PL1_FILE"
        [ -f "$PL2_FILE" ] && echo $((PERFORMANCE_PL2 * MULTIPLIER)) > "$PL2_FILE"
        ;;
esac
