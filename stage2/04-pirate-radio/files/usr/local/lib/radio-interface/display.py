"""The class that implements the display for the screen device."""
import asyncio
import time
from colorsys import hsv_to_rgb

from PIL import Image, ImageDraw, ImageFont
from ST7789 import ST7789

from controls import Controls
from helpers import local_ip_address, playing

BG_COLOR = (255, 255, 0)
TEXT_COLOR = (0, 0, 0)
SCROLL_SPEED = 90
SPI_SPEED_MHZ = 80

controls = Controls()


class Display:
    """Implements the display."""

    def __init__(self) -> None:
        self.display = ST7789(
            rotation=90,  # Needed to display the right way up on Pirate Audio
            port=0,  # SPI port
            cs=1,  # SPI port Chip-select channel
            dc=9,  # BCM pin used for data/command
            backlight=13,
            spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000,
        )
        self.image = Image.new("RGB", (240, 240), BG_COLOR)
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30
        )
        self.current_stream = ""
        self.metadata_queue = asyncio.Queue()  # type: asyncio.Queue

    async def screen_display(self) -> None:
        """
        Listens to the various display queues and displays their
        messages on the screen.
        """
        text_x = self.display.width
        time_start = time.time()
        while True:
            text = self.current_stream
            x = (time.time() - time_start) * SCROLL_SPEED
            size_x, size_y = self.draw.textsize(text, self.font)
            x %= size_x + self.display.width
            self.draw.rectangle(
                (0, 0, self.display.width, self.display.height), BG_COLOR
            )
            text_y = (self.display.height - size_y) // 2
            self.draw.text(
                (int(text_x - x), text_y), text, font=self.font, fill=TEXT_COLOR
            )
            self.display.display(self.image)
            await asyncio.sleep(0.1)

    async def current_stream_display(self) -> None:
        """
        Update the currently playing display from MPD.
        """
        while True:
            name = playing("name")
            title = playing("title")
            text = ""
            if name:
                text += name + " // "
            if title:
                text += title
            self.current_stream = text
            await asyncio.sleep(1)
