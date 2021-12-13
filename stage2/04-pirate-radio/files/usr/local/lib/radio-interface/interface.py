"""This module is a systemd service that takes care of interfacing the
physical interaction devices (buttons, LEDs...) and the controls of the
radio.
"""
import asyncio

import systemd.daemon
from gpiozero import Button

from audio import Audio
from display import Display
from system import System

audio = Audio()
display = Display()
system = System()

# Set the audio volume to a reasonable amount for the first boot
if system.first_boot():
    audio.set_volume(35)

# Make sure the client is playing and in repeat mode on startup
audio.play()
audio.repeat(True)

# all initialization is considered done after this point and we tell
# systemd that we are ready to serve
systemd.daemon.notify("READY=1")

# Assign the buttons to their corresponding GPIOs
fast_forward_button = Button(5)
play_pause_button = Button(6)
volume_up_button = Button(16)
volume_down_button = Button(24)
on_off_button = Button(17)
rewind_button = Button(13)

# Define what actions to set for each button event
fast_forward_button.when_pressed = audio.next
rewind_button.when_pressed = audio.previous
play_pause_button.when_released = audio.play_pause
play_pause_button.when_held = display.ip_address
volume_up_button.when_pressed = audio.volume_up
volume_down_button.when_pressed = audio.volume_down
on_off_button.when_released = system.shutdown
on_off_button.when_held = system.sleep_timer


async def main():
    await asyncio.gather(
        audio.volume_knob(),
        display.current_stream(),
        display.screen(),
    )


asyncio.run(main())
