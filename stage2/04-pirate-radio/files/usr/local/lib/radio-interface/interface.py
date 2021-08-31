"""This module is a systemd service that takes care of interfacing the
physical interaction devices (buttons, LEDs...) and the controls of the
radio.
"""
import asyncio
from signal import pause

import systemd.daemon
from controls import Controls
from gpiozero import Button
from mpd.base import CommandError

controls = Controls()
# if the playlist is empty and an .m3u file has been provided then initialize
with controls.connection_to_mpd():
    if not controls.mpd.playlist():
        try:
            controls.mpd.load("my-playlist")
        except CommandError:
            pass

# Make sure the client is playing and in repeat mode on startup
with controls.connection_to_mpd():
    controls.mpd.play()
    controls.mpd.repeat(1)

# all initialization is considered done after this point and we tell
# systemd that we are ready to serve
systemd.daemon.notify("READY=1")

# Retain compatibility with phat-beat buttons
phatbeat_fast_forward_gpio = 5
phatbeat_rewind_gpio = 13
phatbeat_play_pause_gpio = 6
phatbeat_volume_up_gpio = 16
phatbeat_volume_down_gpio = 26
phatbeat_on_off_button = Button(12)

# Create the buttons by assigning their corresponding GPIOs
fast_forward_button = Button(phatbeat_fast_forward_gpio)
rewind_button = Button(phatbeat_rewind_gpio)
play_pause_button = Button(phatbeat_play_pause_gpio)
volume_up_button = Button(phatbeat_volume_up_gpio)
volume_down_button = Button(phatbeat_volume_down_gpio)
on_off_button = Button(17)

# Define what actions to set for each button event
fast_forward_button.when_pressed = controls.next
rewind_button.when_pressed = controls.previous
play_pause_button.when_pressed = controls.play_pause
volume_up_button.when_pressed = controls.volume_up
volume_down_button.when_pressed = controls.volume_down
on_off_button.when_held = controls.sleep_timer
on_off_button.when_released = controls.shutdown
phatbeat_on_off_button.when_held = controls.sleep_timer
phatbeat_on_off_button.when_released = controls.shutdown

# sync the volume with the potentiometer value
asyncio.run(controls.volume_knob())

# maintain the module loaded for as long the the interface is needed
# without consuming resources
pause()
