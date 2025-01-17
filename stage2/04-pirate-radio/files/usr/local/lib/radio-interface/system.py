""" Controller for system actions."""
import os
from subprocess import run

from audio import Audio
from helpers import notify

audio = Audio()


class System:
    """Implements the system actions."""

    def __init__(self) -> None:
        self.power_button_was_held: bool = False

    @notify
    def sleep_timer(self) -> None:
        """Shutdown button tells the system to shutdown 20 minutes from now."""
        # use the trick described here:
        # https://gpiozero.readthedocs.io/en/stable/faq.html
        # #how-do-i-use-button-when-pressed-and-button-when-held-together
        self.power_button_was_held = True
        command = """shutdown
                   -h +20
                   """
        run(command.split())
        command = """wall
                   -n Sleep timer was triggered. System is shutting down in 20
                   minutes.
                   """
        run(command.split())

    def shutdown(self, button) -> None:
        """Shutdown button tells the system to shutdown now."""
        if not self.power_button_was_held:
            audio.stop()
            command = """shutdown
                    -h now
                    """
            run(command.split())
            command = """wall
                        -n Power off was triggered by user.
                       """
            run(command.split())
        self.power_button_was_held = False

    def first_boot(self) -> bool:
        """Return True if the system is booted for the first time.
        False otherwise.
        """
        if os.path.exists("/transistor_first_boot"):
            os.remove("/transistor_first_boot")
            return True
        return False
