"""This module is a systemd service that takes care of interfacing the
physical interaction devices (buttons, LEDs...) and the controls of the
radio.
"""
import asyncio

import systemd.daemon
from gpiozero import Button

from controls import Controls
from display import Display

controls = Controls()
display = Display()

# Make sure the client is playing and in repeat mode on startup
controls.play()
controls.repeat(True)

# all initialization is considered done after this point and we tell
# systemd that we are ready to serve
systemd.daemon.notify("READY=1")

# Assign the buttons to their corresponding GPIOs
fast_forward_button = Button(5)
rewind_button = Button(13)
play_pause_button = Button(6)
volume_up_button = Button(16)
volume_down_button = Button(24)
on_off_button = Button(17)

# Define what actions to set for each button event
fast_forward_button.when_pressed = controls.next
rewind_button.when_pressed = controls.previous
play_pause_button.when_pressed = controls.play_pause
volume_up_button.when_pressed = controls.volume_up
volume_down_button.when_pressed = controls.volume_down
on_off_button.when_held = controls.sleep_timer
on_off_button.when_released = controls.shutdown


async def main():
    await asyncio.gather(
        controls.volume_knob(),
        display.current_stream_display(),
        display.screen_display(),
    )


asyncio.run(main())
