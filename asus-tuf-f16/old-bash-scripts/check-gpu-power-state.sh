cat /proc/driver/nvidia/gpus/0000:01:00.0/power
cat /sys/bus/pci/devices/0000:01:00.0/power/control
cat /sys/bus/pci/devices/0000:01:00.0/power/runtime_status
nvidia-smi -q -d POWER
nvidia-smi
