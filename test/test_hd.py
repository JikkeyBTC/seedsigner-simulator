"""Display-only HD regression tests; runs with native Pillow or Pyodide 10.2.

Run ``python test/test_hd.py``. The bundled firmware ZIP supplies the exact
fonts, so these checks do not depend on fonts installed on the host.
"""

import importlib.util
import io
import sys
import types
import unittest
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT_ZIP = ROOT / "build/out/wallet-smartcard.zip"
with zipfile.ZipFile(FONT_ZIP) as archive:
    ICON_BYTES = archive.read("seedsigner/resources/fonts/Font_Awesome_6_Free-Solid-900.otf")
    TEXT_BYTES = archive.read("seedsigner/resources/fonts/OpenSans-SemiBold.ttf")


def font(size=18, icon=False):
    return ImageFont.truetype(io.BytesIO(ICON_BYTES if icon else TEXT_BYTES), size)


def scene():
    """Representative firmware operations, including its existing supersampling."""
    canvas = Image.new("RGB", (240, 240), "#080808")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((9, 38, 229, 92), radius=8, fill="#333333", outline="#eeeeee", width=2)
    draw.text((32.5, 69.5), "\uf053", font=font(22, True), fill="white", anchor="ls")
    draw.text((143, 73), "Settings", font=font(22), fill="white", anchor="ms")
    draw.line(((10, 100), (60, 115), (120, 98)), fill="orange", width=3, joint="curve")
    draw.ellipse((185, 101, 199, 115), fill="green", outline="white", width=1)
    draw.arc((207, 98, 230, 121), 20, 270, fill="blue", width=2)
    text = Image.new("RGBA", (440, 100), "#080808")
    ImageDraw.Draw(text).text((220, 60), "Agjpqy 1,234 sats", font=font(36), anchor="ms", fill="#ffffff")
    text = text.resize((220, 50), Image.Resampling.LANCZOS).filter(ImageFilter.SHARPEN)
    canvas.paste(text.crop((0, 10, 220, 45)), (10, 135))
    overlay = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle((0, 200, 239, 239), fill=(255, 0, 0, 90))
    return Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")


# Capture original behavior before install() patches any drawing methods.
NATIVE_BYTES = scene().tobytes()
NATIVE_METRICS = (font(22).getbbox("Agjpqy"), font(22).getlength("Agjpqy"))
_HD = None


class HDTests(unittest.TestCase):
    def hd(self):
        global _HD
        path = ROOT / "src/shims/browser_hd.py"
        self.assertTrue(path.exists(), "the HD sidecar renderer has not been implemented")
        if _HD is None:
            spec = importlib.util.spec_from_file_location("browser_hd", path)
            _HD = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = _HD
            spec.loader.exec_module(_HD)
        _HD.install(scale=8)
        return _HD

    def test_native_pixels_and_metrics_are_unchanged(self):
        hd = self.hd()
        image = scene()
        self.assertEqual(image.size, (240, 240))
        self.assertEqual(image.tobytes(), NATIVE_BYTES)
        self.assertEqual((font(22).getbbox("Agjpqy"), font(22).getlength("Agjpqy")), NATIVE_METRICS)
        output = hd.render(image)
        self.assertEqual(output.size, (1920, 1920))
        self.assertEqual(image.tobytes(), NATIVE_BYTES)
        self.assertNotEqual(output.tobytes(), image.resize(output.size, Image.Resampling.NEAREST).tobytes())

    def test_icon_ink_bounds_survive_fractional_positions_and_clipping(self):
        hd = self.hd()
        for xy in ((32, 41), (32.5, 41.5), (-2.5, 41.5)):
            with self.subTest(xy=xy):
                image = Image.new("L", (240, 240))
                ImageDraw.Draw(image).text(xy, "\uf053", font=font(22, True), fill=255, anchor="ls")
                output = hd.render(image)
                self.assertEqual(output.getbbox(), tuple(v * 8 for v in image.getbbox()))
                self.assertNotEqual(output.tobytes(), image.resize(output.size, Image.Resampling.NEAREST).tobytes())

    def test_inclusive_rectangles_and_rounded_native_crop(self):
        hd = self.hd()
        image = Image.new("L", (20, 20))
        ImageDraw.Draw(image).rectangle((1.75, 1.75, 3.75, 3.75), fill=255)
        output = hd.render(image)
        self.assertEqual(output.getbbox(), (8, 8, 32, 32))
        cropped = image.crop((1.75, 1.75, 6.5, 6.5))
        self.assertEqual(cropped.size, (4, 4))
        self.assertEqual(hd.render(cropped).tobytes(), output.crop((16, 16, 48, 48)).tobytes())

    def test_paste_captures_source_state_before_later_mutation(self):
        hd = self.hd()
        source = Image.new("RGB", (30, 30), "black")
        draw = ImageDraw.Draw(source)
        draw.rectangle((2, 3, 9, 11), fill="white")
        canvas = Image.new("RGB", (60, 60), "black")
        canvas.paste(source, (10, 12))
        saved = canvas.copy()
        draw.rectangle((0, 0, 29, 29), fill="red")
        canvas.paste(canvas)
        self.assertEqual(hd.render(canvas).tobytes(), hd.render(saved).tobytes())
        self.assertEqual(hd.render(canvas).getpixel((13 * 8, 16 * 8)), (255, 255, 255))

    def test_masked_paste_and_alpha_composite_keep_transparency(self):
        hd = self.hd()
        base = Image.new("RGBA", (40, 40), "blue")
        ImageDraw.Draw(base).rectangle((0, 0, 0, 0), fill="blue")
        overlay = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
        ImageDraw.Draw(overlay).rectangle((3, 4, 14, 15), fill=(255, 0, 0, 128))
        base.paste(overlay, (10, 10), overlay)
        result = hd.render(base)
        self.assertEqual(result.getpixel((0, 0)), base.getpixel((0, 0)))
        self.assertEqual(result.getpixel((15 * 8, 16 * 8)), base.getpixel((15, 16)))
        composite = Image.alpha_composite(base, Image.new("RGBA", base.size, (0, 255, 0, 30)))
        self.assertEqual(hd.render(composite).getpixel((15 * 8, 16 * 8)), composite.getpixel((15, 16)))

    def test_untagged_qr_bitmap_is_expanded_exactly_with_nearest_sampling(self):
        hd = self.hd()
        data = bytes(255 if (x // 3 + y // 3) % 2 else 0 for y in range(27) for x in range(27))
        qr = Image.frombytes("L", (27, 27), data)
        expected = qr.resize((216, 216), Image.Resampling.NEAREST)
        self.assertEqual(hd.render(qr).tobytes(), expected.tobytes())
        canvas = Image.new("L", (40, 40), 127)
        ImageDraw.Draw(canvas).text((0, 39), "A", font=font(8), fill=255, anchor="ls")
        canvas.paste(qr, (5, 3))
        self.assertEqual(hd.render(canvas).crop((40, 24, 256, 240)).tobytes(), expected.tobytes())

    def test_qrcode_library_color_masks_remain_native_bitmaps(self):
        hd = self.hd()
        sys.path.insert(0, str(FONT_ZIP))
        try:
            import qrcode
            from qrcode.image.styledpil import StyledPilImage
            from qrcode.image.styles.moduledrawers import CircleModuleDrawer
            qr = qrcode.QRCode(version=1, box_size=5, border=3)
            qr.add_data("HD display test")
            qr.make(fit=True)
            image = qr.make_image(fill_color="black", back_color="white", image_factory=StyledPilImage,
                                  module_drawer=CircleModuleDrawer()).get_image()
            expected = image.resize((image.width * 8, image.height * 8), Image.Resampling.NEAREST)
            self.assertEqual(hd.render(image).tobytes(), expected.tobytes())
        finally:
            sys.path.remove(str(FONT_ZIP))

    def test_nested_supersampling_and_large_crop_remain_vector_drawn(self):
        hd = self.hd()
        chart = Image.new("RGB", (960, 320), "black")
        ImageDraw.Draw(chart).text((480, 160), "1,234 sats", font=font(72), fill="white", anchor="ms")
        chart = chart.resize((240, 80), Image.Resampling.LANCZOS).filter(ImageFilter.SHARPEN)
        rendered = hd.render(chart)
        self.assertEqual(rendered.size, (1920, 640))
        self.assertNotEqual(rendered.tobytes(), chart.resize(rendered.size, Image.Resampling.NEAREST).tobytes())
        large = Image.new("L", (888, 888), 255)
        ImageDraw.Draw(large).rectangle((300, 300, 330, 330), fill=0)
        visible = large.crop((240, 240, 480, 480))
        self.assertEqual(hd.render(visible).size, (1920, 1920))
        self.assertEqual(hd.render(visible).getpixel((60 * 8, 60 * 8)), 0)

    def test_pixel_mutations_invalidate_recorded_drawing(self):
        hd = self.hd()
        image = Image.new("RGB", (20, 20), "black")
        ImageDraw.Draw(image).rectangle((0, 0, 19, 19), fill="white")
        image.putpixel((3, 4), (255, 0, 0))
        self.assertEqual(hd.render(image).getpixel((24, 32)), (255, 0, 0))

    def test_scrolled_text_uses_the_same_visible_glyph_pixels(self):
        hd = self.hd()
        image = Image.new("L", (600, 60))
        ImageDraw.Draw(image).text((0.5, 48.5), "Review the transaction address and amount", font=font(24), fill=255, anchor="ls")
        full = hd.render(image)
        cropped = image.crop((173, 0, 413, 60))
        self.assertEqual(hd.render(cropped).tobytes(), full.crop((173 * 8, 0, 413 * 8, 60 * 8)).tobytes())

    def test_scale_one_returns_the_exact_native_frame(self):
        hd = self.hd()
        hd.install(scale=1)
        self.assertEqual(hd.render(scene()).tobytes(), NATIVE_BYTES)

    def test_install_scale_is_configurable_and_idempotent(self):
        hd = self.hd()
        hd.install(scale=4)
        hd.install(scale=4)
        image = Image.new("L", (10, 10))
        ImageDraw.Draw(image).rectangle((1, 1, 3, 3), fill=255)
        self.assertEqual(hd.render(image).size, (40, 40))
        self.assertEqual(hd.render(image).getbbox(), (4, 4, 16, 16))
        with self.assertRaises(ValueError):
            hd.install(scale=0)

    def test_repeated_complete_frames_keep_their_hd_drawing(self):
        hd = self.hd()
        image = Image.new("L", (80, 40))
        ImageDraw.Draw(image).text((4, 28), "Agjpqy", font=font(18), fill=255, anchor="ls")
        expected = hd.render(image).tobytes()
        for _ in range(80):
            image.paste(image)
        self.assertEqual(hd.render(image).tobytes(), expected)
        display = Image.new("L", image.size)
        for _ in range(80):
            display.paste(image)
        self.assertEqual(hd.render(display).tobytes(), expected)

    def test_outside_crop_has_native_zero_padding(self):
        hd = self.hd()
        image = Image.new("L", (10, 10))
        ImageDraw.Draw(image).rectangle((-3, -3, 13, 13), fill=255)
        cropped = image.crop((-2, -2, 12, 12))
        self.assertEqual(hd.render(cropped).tobytes(), cropped.resize((112, 112), Image.Resampling.NEAREST).tobytes())

    def test_display_sink_has_hd_dimensions_and_keeps_native_buffer(self):
        self.hd()
        module_name = "seedsigner.hardware.displays.display_driver"
        if module_name not in sys.modules:
            driver = types.ModuleType(module_name)
            sys.modules[module_name] = driver
            with zipfile.ZipFile(FONT_ZIP) as archive:
                exec(archive.read("seedsigner/hardware/displays/display_driver.py"), driver.__dict__)
        path = ROOT / "src/shims/browser_display.py"
        spec = importlib.util.spec_from_file_location("browser_display", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        frames = []
        display = module.BrowserDisplay(_width=240, _height=240, sink=lambda *args: frames.append(args), hd_scale=8)
        image = Image.new("RGB", (240, 240))
        ImageDraw.Draw(image).text((20, 30), "Settings", font=font(), fill="white")
        native = image.tobytes()
        display.show_image(image)
        self.assertEqual((display.width, display.height), (240, 240))
        self.assertIs(display.buffer, image)
        self.assertEqual(display.buffer.tobytes(), native)
        self.assertEqual(frames[-1][1:], (1920, 1920))
        self.assertEqual(len(frames[-1][0]), 1920 * 1920 * 3)
        display = module.BrowserDisplay(_width=240, _height=240, sink=lambda *args: frames.append(args))
        display.show_image(image)
        self.assertEqual(frames[-1], (native,))


if __name__ == "__main__":
    unittest.main(verbosity=2)
