# PiUSBCamera

This should work OK under BULLSEYE or BOOKWORM, ensure you don't have a Pi Camera connected to your Pi.

Script to allow control of a USB Camera on a Pi, using v4l2-ctl, to allow parameters to be set and still pictures or videos to be taken. 

Shows a reduced preview but saves stills / video at max resolutions or user set.

Videos are video ONLY , NO audio. 

BETA version PiUSBCameraA.py records video with Audio, set Video time with right click on Capture button.

Click mouse on the left of a button to decrease, right to increase

Click on image to restore camera default settings

Should detect the USB camera and set the appropriate control buttons.

To get it to work under Bullseye try...

sudo apt install libsdl2-ttf-2.0-0

and if using Buster or Bullseye (not Bookworm)

python3 -m pip install -U pygame --user

## Screenshot

![screenshot](screenshot.jpg)
