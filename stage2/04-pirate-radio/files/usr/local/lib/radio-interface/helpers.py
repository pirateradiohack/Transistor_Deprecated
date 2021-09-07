from functools import wraps

import simpleaudio as sa

SLEEP_TIMER_SOUND = "/usr/local/lib/radio-interface/sleep-timer.wav"


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
