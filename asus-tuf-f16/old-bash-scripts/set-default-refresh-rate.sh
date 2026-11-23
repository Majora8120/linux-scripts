#!/bin/bash
kscreen-doctor output.eDP-1.mode.1920x1200@60
asusctl armoury set panel_overdrive 0
# Forces a display refresh by changing color accuracy which fixes 60hz feeling very slow
kscreenctl eDP-1 set-color-power-tradeoff prefer-efficiency && kscreenctl eDP-1 set-color-power-tradeoff prefer-accuracy
