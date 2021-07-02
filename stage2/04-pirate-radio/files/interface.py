"""This module is a systemd service that takes care of interfacing the
physical interaction devices (buttons, LEDs...) and the software of the
radio.
"""
import asyncio
from contextlib import contextmanager
from signal import pause
from subprocess import run

import alsaaudio
import pulsectl
import simpleaudio as sa
import systemd.daemon
from gpiozero import MCP3008, Button
from mpd import MPDClient
from mpd.base import CommandError

HOST, PORT = "localhost", 6600
VOLUME_STEP = 10

# Retain compatibility with phat-beat buttons
PHATBEAT_BUTTON_FAST_FORWARD = 5
PHATBEAT_BUTTON_REWIND = 13
PHATBEAT_BUTTON_PLAY_PAUSE = 6
PHATBEAT_BUTTON_VOLUME_UP = 16
PHATBEAT_BUTTON_VOLUME_DOWN = 26
PHATBEAT_BUTTON_ON_OFF = Button(12)

POTENTIOMETER_VOLUME = MCP3008(0)

SLEEP_TIMER_SOUND = "/usr/local/lib/radio-interface/sleep-timer.wav"

client = MPDClient()


@contextmanager
def connection_to_mpd():
    """Context manager to establish the connection with MPD.

    Should be used for every use of the client since the connection is
    sketchy.
    """
    try:
        client.connect(HOST, PORT)
        yield
    finally:
        client.close()
        client.disconnect()


# if the playlist is empty and an .m3u file has been provided then initialize
with connection_to_mpd():
    if not client.playlist():
        try:
            client.load("my-playlist")
        except (CommandError):
            pass

# Make sure we are not in the stop position (does not affect pause)
# and make sure we are in repeat mode to avoid falling in the stopped
# position when we hit the end of the playlist by pushing next on the
# last radio station of the playlist.
with connection_to_mpd():
    client.play()
    client.repeat(1)

# all initialization is considered done after this point and we tell
# systemd that we are ready to serve
systemd.daemon.notify("READY=1")


def volume_down():
    """Volume down button tells pulseaudio to step down the volume."""
    command = """pactl
                set-sink-volume
                0
                -{}%
                """.format(
        VOLUME_STEP
    )
    run(command.split())


def volume_up():
    """Volume up button tells pulseaudio to step up the volume."""
    command = """pactl
                set-sink-volume
                0
                +{}%
                """.format(
        VOLUME_STEP
    )
    run(command.split())


def play_pause():
    """Play/pause button tells MPD to toggle play/plause."""
    with connection_to_mpd():
        client.pause()


def next_station():
    """Next button tells MPD to play next track."""
    with connection_to_mpd():
        client.next()


def previous_station():
    """Previous button tells MPD to play previous track."""
    with connection_to_mpd():
        client.previous()


# use the trick described here
# https://gpiozero.readthedocs.io/en/stable/faq.html
# #how-do-i-use-button-when-pressed-and-button-when-held-together
Button.was_held = False


def sleep_timer(button):
    """Shutdown button tells the system to shutdown 20 minutes from now."""
    button.was_held = True
    command = """shutdown
               -h +20
               """
    run(command.split())
    command = """wall
               -n Power off button was held. System is shutting down in 20
               minutes
               """
    run(command.split())
    # play a sound to inform the user that the long button press is
    # registered
    wave_obj = sa.WaveObject.from_wave_file(SLEEP_TIMER_SOUND)
    # simpleaudio goes straight through alsa
    # so we need to use alsa in order to control the beep volume
    sound_mixer = alsaaudio.Mixer()
    sound_mixer.setvolume(35)
    play_obj = wave_obj.play()
    play_obj.wait_done()
    sound_mixer.setvolume(100)


def shutdown(button):
    """Shutdown button tells the system to shutdown now."""
    if not button.was_held:
        command = """shutdown
                -h now
                """
        run(command.split())
        command = """wall
                    -n Power off button was released
                   """
        run(command.split())
    button.was_held = False


async def volume():
    """
    Set the volume according to the potentiometer.
    Gpiozero returns a float from 0 to 1 from the potentiometer.
    It can be fed directly into pulse audio, 1 being the maximum
    volume (above 1 is the soft boost).
    """
    # Create a client for Pulse Audio
    pulse = pulsectl.Pulse("volume")
    # Choose the sink we want to set the volume to
    sink = pulse.sink_list()[0]
    while True:
        volume = POTENTIOMETER_VOLUME.value
        pulse.volume_set_all_chans(sink, volume)
        await asyncio.sleep(0.1)


# Set the pins to which buttons are connected
BUTTON_FAST_FORWARD = Button(PHATBEAT_BUTTON_FAST_FORWARD)
BUTTON_REWIND = Button(PHATBEAT_BUTTON_REWIND)
BUTTON_PLAY_PAUSE = Button(PHATBEAT_BUTTON_PLAY_PAUSE)
BUTTON_VOLUME_UP = Button(PHATBEAT_BUTTON_VOLUME_UP)
BUTTON_VOLUME_DOWN = Button(PHATBEAT_BUTTON_VOLUME_DOWN)
BUTTON_ON_OFF = Button(17)

# Define what actions to set for each button event
BUTTON_FAST_FORWARD.when_pressed = next_station
BUTTON_REWIND.when_pressed = previous_station
BUTTON_PLAY_PAUSE.when_pressed = play_pause
BUTTON_VOLUME_UP.when_pressed = volume_up
BUTTON_VOLUME_DOWN.when_pressed = volume_down
BUTTON_ON_OFF.when_held = sleep_timer
BUTTON_ON_OFF.when_released = shutdown
PHATBEAT_BUTTON_ON_OFF.when_pressed = shutdown

# set pulseaudio volume to POTENTIOMETER_VOLUME.value
asyncio.run(volume())

# maintain the module loaded for as long the the interface is needed
# without conuming resources
pause()
