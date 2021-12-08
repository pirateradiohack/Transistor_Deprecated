"""Helper functions for the controllers."""
from contextlib import contextmanager
from functools import wraps

import netifaces

import pulsectl
import simpleaudio as sa
from mpd import MPDClient

SLEEP_TIMER_SOUND = "/usr/local/lib/radio-interface/sleep-timer.wav"
MPD_HOST, MPD_PORT = "localhost", 6600


def notify(function):
    """
    Play a sound to inform the user that an action has been registered.
    To be used as a decorator.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        sleep_timer_sound = sa.WaveObject.from_wave_file(SLEEP_TIMER_SOUND)
        notification = sleep_timer_sound.play()
        return function(*args, **kwargs)
        notification.wait_done()

    return wrapper


@contextmanager
def connection_to_mpd():
    """Context manager to establish the connection with MPD."""
    mpd = MPDClient()
    try:
        mpd.timeout = 10
        mpd.idletimeout = None
        mpd.connect(MPD_HOST, MPD_PORT)
        yield mpd
    finally:
        mpd.close()
        mpd.disconnect()


@contextmanager
def connection_to_pulseaudio():
    """Context manager to establish a connection with Pulse Audio.

    Should be used each time getting the volume is necessary since the
    client is not synchronized when the volume is changed on another
    client.
    That is necessary for instance when changing the volume as the current
    volume is needed in order to apply a change.
    """
    try:
        pulse_client = pulsectl.Pulse("radio-interface")
        pulse_sink = pulse_client.sink_list()[0]
        yield {"client": pulse_client, "sink": pulse_sink}
    finally:
        pulse_client.close()


def local_ip_address() -> str:
    """Return local IP address."""
    ip_address = netifaces.ifaddresses('wlan0')
    ip_address = ip_address[netifaces.AF_INET]
    ip_address = ip_address[0].get('addr')
    return ip_address


def playing(content: str) -> str:
    """Fetch the currently playing content.

    Available content is:
    - name
    - album
    - artist
    - title
    """
    with connection_to_mpd() as mpd:
        playing = mpd.currentsong()
    return playing.get(content)
