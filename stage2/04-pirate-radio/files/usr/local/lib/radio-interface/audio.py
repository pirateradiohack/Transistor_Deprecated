"""The class that implements the controller for the audio device."""
import asyncio

from gpiozero import MCP3008, Button

from helpers import (
    connection_to_mpd,
    connection_to_pulseaudio,
)

VOLUME_STEP = 0.05
POTENTIOMETER_THRESHOLD_TRIGGER = 0.01


class Audio:
    """Implements the various controls needed in an audio device."""

    play_pause_button_was_held: bool = False

    def __init__(self) -> None:
        self.potentiometer_volume = MCP3008(0)

    def set_volume(self, amount: int) -> None:
        """Set audio volume amount in percent."""
        with connection_to_pulseaudio() as pulse:
            pulse['client'].volume_set_all_chans(pulse['sink'], amount / 100)

    def volume_down(self) -> None:
        """Volume down button tells pulseaudio to step down the volume."""
        with connection_to_pulseaudio() as pulse:
            pulse["client"].volume_change_all_chans(pulse["sink"], -VOLUME_STEP)

    def volume_up(self) -> None:
        """Volume up button tells pulseaudio to step up the volume."""
        with connection_to_pulseaudio() as pulse:
            pulse["client"].volume_change_all_chans(pulse["sink"], +VOLUME_STEP)

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
            knob_movement = (
                abs(self.potentiometer_volume.value - comparison_point)
                > POTENTIOMETER_THRESHOLD_TRIGGER
            )
            if knob_movement:
                volume = self.potentiometer_volume.value
                with connection_to_pulseaudio() as pulse:
                    pulse["client"].volume_set_all_chans(pulse["sink"], volume)
            comparison_point = self.potentiometer_volume.value
            await asyncio.sleep(0.1)

    def play(self) -> None:
        """Start audio playback."""
        with connection_to_mpd() as mpd:
            mpd.play()

    def stop(self) -> None:
        """Stop audio playback."""
        with connection_to_mpd() as mpd:
            mpd.stop()

    def repeat(self, state: bool) -> None:
        """Select repeat mode for the playlist.

        Options for state are:
        - True
        - False
        """
        if state:
            state = 1
        else:
            state = 0
        with connection_to_mpd() as mpd:
            mpd.repeat(state)

    def play_pause(self) -> None:
        """Toggle play/pause."""
        if not Audio.play_pause_button_was_held:
            with connection_to_mpd() as mpd:
                mpd.pause()
        Audio.play_pause_button_was_held = False

    def next(self) -> None:
        """Play next track."""
        with connection_to_mpd() as mpd:
            mpd.next()

    def previous(self) -> None:
        """Play previous track."""
        with connection_to_mpd() as mpd:
            mpd.previous()
