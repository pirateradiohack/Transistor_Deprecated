"""The class that implements the display for the screen device."""
import asyncio
import time
from colorsys import hsv_to_rgb

from PIL import Image, ImageDraw, ImageFont
from ST7789 import ST7789

from controls import Controls

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

    async def metadata_display(self) -> None:
        """
        Takes the currently playing metadata from MPD and displays
        it on the screen."""
        text_x = self.display.width
        time_start = time.time()
        while True:
            name = controls.playing("name")
            title = controls.playing("title")
            text = ""
            if name:
                text += name + ' // '
            if title:
                text += title
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
