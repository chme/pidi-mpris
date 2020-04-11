# Control MPRIS media players with a Pirate Audio Raspberry Pi add-on

__pidi-mpris__ allows you to control a MPRIS capable media player with 
a [Pirate Audio Raspberry Pi add-on](https://shop.pimoroni.com/collections/pirate-audio).


It displays the album cover art for the current song on the Pirate Audio display 
([ST7789 display](https://github.com/pimoroni/st7789-python)) and assigns playback control
commands to the four buttons A, B, X and Y (active low connected to BCM 5, 6, 16, and 20.


Tested on a headless Raspberry Pi 3 A+ to control [Shairport Sync](https://github.com/mikebrady/shairport-sync).


__Button Mapping__

| Button | Artwork Screen | Info Screen | Gif Screen |
| ------ | -------------- | ----------- | ---------- |
| A      | Skip to previous song | Skip to previous song | _not assigned_ |
| B      | Show next screen | Show next screen | Show next screen |
| B (long press 3s) | Turn display off/on | Turn display off/on | Turn display off/on |
| X      | Skip to next song | Skip to next song | _not assigned_ |
| Y      | Toggle play / pause | Toggle play / pause | Cycle through configured gif images |
