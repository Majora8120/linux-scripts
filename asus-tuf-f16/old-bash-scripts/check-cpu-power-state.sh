#!/bin/bash
# Check PL1 (Sustained Power)
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
# Check PL2 (Short Burst Power)
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_1_power_limit_uw
