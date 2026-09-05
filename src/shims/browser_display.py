"""
A SeedSigner display driver that draws to a browser canvas.

Mirrors the fork's desktop_display.py, but where that one pushes frames into a
pygame window this one hands raw RGB bytes to JavaScript. Everything above it,
the Renderer and every screen, is unmodified SeedSigner.
"""

from dataclasses import dataclass

from PIL import Image

from seedsigner.hardware.displays.display_driver import BaseDisplayDriver


@dataclass
class BrowserDisplay(BaseDisplayDriver):
    """
    `_width` and `_height` come from BaseDisplayDriver and describe the emulated
    panel. `sink` is a callback supplied by the worker that forwards a frame to
    the page.
    """

    sink: object = None
    hd_scale: int = None

    def __post_init__(self):
        # Opt-in before Renderer creates its canvas. The physical panel and
        # every image visible to the firmware retain their native dimensions.
        self._hd = None
        if self.hd_scale is not None:
            import browser_hd
            browser_hd.install(scale=self.hd_scale)
            self._hd = browser_hd
        self.buffer = Image.new("RGB", (self.width, self.height))
        self.inverted = False

    def invert(self, enabled: bool = True):
        # The real panel inverts in hardware; there is nothing to do here, and
        # the colours already arrive the right way round.
        self.inverted = enabled

    def show_image(self, image: Image.Image, x_start: int = 0, y_start: int = 0):
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))
        if image.mode != "RGB":
            image = image.convert("RGB")

        self.buffer = image
        if self.sink is not None:
            if self._hd is not None:
                frame = self._hd.render(image)
                self.sink(frame.tobytes(), frame.width, frame.height)
            else:
                self.sink(image.tobytes())

    def ShowImage(self, image, x_start: int = 0, y_start: int = 0):
        """Some drivers in this codebase use the capitalised spelling."""
        self.show_image(image, x_start, y_start)

    def clear(self):
        self.show_image(Image.new("RGB", (self.width, self.height)))

    def cleanup(self):
        pass


def install(sink, width: int, height: int, hd_scale: int = None) -> None:
    """
    Make the factory hand back a BrowserDisplay whatever the configured display
    type is, so the wallet's own settings do not have to be touched. When
    hd_scale is set, sink receives (RGB bytes, frame width, frame height).
    Otherwise its existing one-argument contract is preserved.
    """
    from seedsigner.hardware.displays import display_driver

    def instantiate(cls, display_type=None, width=width, height=height):
        return BrowserDisplay(_width=width, _height=height, sink=sink, hd_scale=hd_scale)

    display_driver.DisplayDriverFactory.instantiate_display_driver = classmethod(instantiate)
