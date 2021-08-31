"""The class that implements the controls for the audio device."""
import asyncio
from contextlib import contextmanager
from subprocess import run

import pulsectl
import simpleaudio as sa
from gpiozero import MCP3008, Button
from mpd import MPDClient

VOLUME_STEP = 0.1
SLEEP_TIMER_SOUND = "/usr/local/lib/radio-interface/sleep-timer.wav"
HOST, PORT = "localhost", 6600
POTENTIOMETER_THRESHOLD_TRIGGER = 0.01
# use the trick described here:
# https://gpiozero.readthedocs.io/en/stable/faq.html
# #how-do-i-use-button-when-pressed-and-button-when-held-together
Button.was_held = False


class Controls:
    """Implements the various controls needed in an audio device.

    mpd client, pulse client and potentiometer_volume are class variable
    because these resources are better to be shared by all instances of
    the Controls class. (Even though a typical use case won't require
    more than 1 instance of the class.)
    """

    mpd = MPDClient()
    pulse_client = pulsectl.Pulse("volume")
    potentiometer_volume = MCP3008(0)

    def __init__(self) -> None:
        self.button_was_held: bool = False
        self.pulse_sink = self.pulse_client.sink_list()[0]

    @contextmanager
    def connection_to_mpd(self):
        """Context manager to establish the connection with MPD.

        Should be used for every use of the client since the connection is
        sketchy.
        """
        try:
            self.mpd.connect(HOST, PORT)
            yield
        finally:
            self.mpd.close()
            self.mpd.disconnect()

    def volume_down(self) -> None:
        """Volume down button tells pulseaudio to step down the volume."""
        self.pulse_client.volume_change_all_chans(self.pulse_sink, -VOLUME_STEP)

    def volume_up(self) -> None:
        """Volume up button tells pulseaudio to step up the volume."""
        self.pulse_client.volume_change_all_chans(self.pulse_sink, +VOLUME_STEP)

    async def volume_knob(self) -> None:
        """
        Set the volume according to the potentiometer.
        Gpiozero returns a float from 0 to 1 from the potentiometer.
        It can be fed directly into pulse audio, 1 being the maximum
        volume (above 1 is the soft boost).

        The potentiometer has an electrical charge that varies
        enough to constantly trigger a volume change.
        We make sure we only trigger the volume change when the
        volume knob is actually moved.
        That also helps in the use case when the volume is set by
        other means, like the web interface, it avoids the
        situation where the volume knob would cancel the volume
        change by constantly setting it back to its own level.

        The potentiometer value moves roughly by more or less 0.01.
        """
        comparison_point = self.potentiometer_volume.value
        while True:
            if (
                abs(self.potentiometer_volume.value - comparison_point)
                > POTENTIOMETER_THRESHOLD_TRIGGER
            ):
                volume = self.potentiometer_volume.value
                self.pulse_client.volume_set_all_chans(self.pulse_sink, volume)
            comparison_point = self.potentiometer_volume.value
            await asyncio.sleep(0.1)

    def play_pause(self) -> None:
        """Play/pause button tells MPD to toggle play/pause."""
        with self.connection_to_mpd():
            self.mpd.pause()

    def next(self) -> None:
        """Next button tells MPD to play next track."""
        with self.connection_to_mpd():
            self.mpd.next()

    def previous(self) -> None:
        """Previous button tells MPD to play previous track."""
        with self.connection_to_mpd():
            self.mpd.previous()

    def sleep_timer(self, button) -> None:
        """Shutdown button tells the system to shutdown 20 minutes from now."""
        self.button_was_held = True
        command = """shutdown
                   -h +20
                   """
        run(command.split())
        command = """wall
                   -n Sleep timer was triggered. System is shutting down in 20
                   minutes.
                   """
        run(command.split())
        self._notify()

    def _notify(self) -> None:
        """
        Play a sound to inform the user that the long button press is
        registered.
        """
        sleep_timer_sound = sa.WaveObject.from_wave_file(SLEEP_TIMER_SOUND)
        notification = sleep_timer_sound.play()
        notification.wait_done()

    def shutdown(self, button) -> None:
        """Shutdown button tells the system to shutdown now."""
        if not self.button_was_held:
            with self.connection_to_mpd():
                self.mpd.stop()
            command = """shutdown
                    -h now
                    """
            run(command.split())
            command = """wall
                        -n Power off was triggered by user.
                       """
            run(command.split())
        self.button_was_held = False
