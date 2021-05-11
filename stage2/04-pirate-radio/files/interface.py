"""This module is a systemd service that takes care of interfacing the
physical interaction devices (buttons, LEDs...) and the software of the
radio.
"""
from subprocess import run
from contextlib import contextmanager
from signal import pause

from gpiozero import Button
import systemd.daemon
from mpd import MPDClient
from mpd.base import CommandError

HOST, PORT = 'localhost', 6600
VOLUME_STEP = 10

# Retain compatibility with phat-beat buttons
PHATBEAT_BUTTON_FAST_FORWARD = 5
PHATBEAT_BUTTON_REWIND = 13
PHATBEAT_BUTTON_PLAY_PAUSE = 6
PHATBEAT_BUTTON_VOLUME_UP = 16
PHATBEAT_BUTTON_VOLUME_DOWN = 26
PHATBEAT_BUTTON_ON_OFF = Button(12)

# Set the pins to which buttons are connected
BUTTON_FAST_FORWARD = Button(PHATBEAT_BUTTON_FAST_FORWARD)
BUTTON_REWIND = Button(PHATBEAT_BUTTON_REWIND)
BUTTON_PLAY_PAUSE = Button(PHATBEAT_BUTTON_PLAY_PAUSE)
BUTTON_VOLUME_UP = Button(PHATBEAT_BUTTON_VOLUME_UP)
BUTTON_VOLUME_DOWN = Button(PHATBEAT_BUTTON_VOLUME_DOWN)
BUTTON_ON_OFF = Button(17)

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
        except(CommandError):
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
systemd.daemon.notify('READY=1')


def volume_down():
    """Volume down button tells pulseaudio to step down the volume."""
    command = """pactl
                set-sink-volume
                0
                -{}%
                """.format(VOLUME_STEP)
    run(command.split())


def volume_up():
    """Volume up button tells pulseaudio to step up the volume."""
    command = """pactl
                set-sink-volume
                0
                +{}%
                """.format(VOLUME_STEP)
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


def shutdown():
    """Shutdown button tells the system to shutdown now."""
    command = """shutdown
                -h now
                """
    run(command.split())


# Define what actions to set for each button event
BUTTON_FAST_FORWARD.when_pressed = next_station
BUTTON_REWIND.when_pressed = previous_station
BUTTON_PLAY_PAUSE.when_pressed = play_pause
BUTTON_VOLUME_UP.when_pressed = volume_up
BUTTON_VOLUME_DOWN.when_pressed = volume_down
BUTTON_ON_OFF.when_pressed = shutdown
PHATBEAT_BUTTON_ON_OFF.when_pressed = shutdown

# maintain the module loaded for as long the the interface is needed
# without conuming resources
pause()
