# Forces a display refresh by changing color accuracy which fixes 60hz feeling very slow
kscreenctl eDP-1 set-color-power-tradeoff prefer-efficiency && kscreenctl eDP-1 set-color-power-tradeoff prefer-accuracy
