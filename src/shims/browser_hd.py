"""Optional high-resolution display sidecar for the unchanged Pillow renderer.

install() records GUI drawing alongside real, native-size Pillow images. All
original operations still execute, with their original arguments and return
values. render() alone replays the visible composition at a higher resolution.
No font metrics, image bytes, camera data, or firmware coordinates are replaced.

The operation history is immutable: copying/pasting an image captures that
version, not a reference to its future contents. Crops and resizes are deferred
transforms, so a 4x supersampled chart or an oversized QR does not allocate a
32x chart or a full-size HD QR. Only the requested viewport is rasterized.

QR library internals and unsupported raster operations stay native. Existing
SHARPEN filters still affect native pixels; the HD replay omits that small-grid
finishing filter. Unknown operations invalidate their sidecar rather than
silently leaving stale pixels. This module is inactive until install() runs.
"""

from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
import inspect
import logging
import math
import sys

from PIL import Image, ImageDraw, ImageFilter


_ATTR = "_browser_hd_state"
_scale = 8
_installed = False
_busy = 0
_warned = set()
_fonts = OrderedDict()
_MAX_OPS = 512
_MAX_DEPTH = 64
_MAX_GLYPH_PIXELS = 8_000_000

# Keep original entry points, including those used internally by replay.
_NEW = Image.new
_DRAW = ImageDraw.Draw
_COPY = Image.Image.copy
_CROP = Image.Image.crop
_RESIZE = Image.Image.resize
_CONVERT = Image.Image.convert
_PASTE = Image.Image.paste
_TRANSFORM = Image.Image.transform
_ALPHA = Image.alpha_composite


@dataclass(frozen=True)
class _State:
    mode: str
    size: tuple
    base: tuple
    ops: tuple = ()
    depth: int = 0


@contextmanager
def _native():
    global _busy
    _busy += 1
    try:
        yield
    finally:
        _busy -= 1


def _state(image):
    return getattr(image, _ATTR, None)


def _forget(image):
    if hasattr(image, _ATTR):
        delattr(image, _ATTR)


def _warning(error):
    # Do not include arguments, text, seed words, or exception messages.
    name = type(error).__name__
    if name not in _warned:
        _warned.add(name)
        logging.getLogger(__name__).warning("HD display used native pixels after %s", name)


def _snapshot(image):
    state = _state(image)
    if state is not None:
        return state
    return _State(image.mode, image.size, ("raster", _COPY(image)))


def _assign(image, state):
    if state.depth > _MAX_DEPTH or len(state.ops) > _MAX_OPS:
        state = _State(image.mode, image.size, ("raster", _COPY(image)))
    setattr(image, _ATTR, state)


def _record(image, action):
    try:
        with _native():
            action()
    except Exception as error:
        _forget(image)
        _warning(error)


def _flatten(xy):
    if isinstance(xy[0], (tuple, list)):
        return tuple(c for point in xy for c in point)
    return tuple(xy)


def _draw_factory(image, *args, **kwargs):
    if _busy:
        return _DRAW(image, *args, **kwargs)
    caller = sys._getframe(1).f_globals.get("__name__", "")
    with _native():
        result = _DRAW(image, *args, **kwargs)
    # qrcode applies raster color masks after drawing (including putpixel).
    # Its finished bitmap is deliberately expanded with NEAREST instead.
    if isinstance(image, Image.Image) and not caller.startswith("qrcode"):
        _record(image, lambda: _assign(image, _snapshot(image)))
    return result


def _draw_method(name, original):
    signature = inspect.signature(original)

    @wraps(original)
    def wrapped(draw, *args, **kwargs):
        if _busy or _state(draw._image) is None:
            return original(draw, *args, **kwargs)
        with _native():
            result = original(draw, *args, **kwargs)

        def record():
            bound = signature.bind(draw, *args, **kwargs)
            bound.apply_defaults()
            values = dict(bound.arguments)
            values.pop("self", None)
            extra = values.pop("kwargs", {})
            positional = values.pop("args", ())
            if extra or positional:
                raise ValueError("unsupported draw extension")
            values["xy"] = _flatten(values["xy"])
            values["_mode"] = draw.mode
            values["_fontmode"] = draw.fontmode
            if name == "text" and (values["font"] is None or "\n" in values["text"]):
                raise ValueError("unsupported text rasterizer")
            current = _state(draw._image)
            if name == "rectangle" and values.get("fill") is not None and draw.mode == draw._image.mode:
                x0, y0, x1, y1 = values["xy"]
                if x0 <= 0 and y0 <= 0 and x1 >= current.size[0] - 1 and y1 >= current.size[1] - 1:
                    current = _State(current.mode, current.size, ("solid", values["fill"]))
            _assign(draw._image, _State(current.mode, current.size, current.base,
                                       current.ops + (("draw", name, values),), current.depth))

        _record(draw._image, record)
        return result

    return wrapped


def _derived_method(name, original):
    signature = inspect.signature(original)

    @wraps(original)
    def wrapped(image, *args, **kwargs):
        if _busy:
            return original(image, *args, **kwargs)
        source = _state(image)
        with _native():
            result = original(image, *args, **kwargs)
        if source is None:
            return result

        def record():
            values = dict(signature.bind(image, *args, **kwargs).arguments)
            values.pop("self", None)
            if name == "copy":
                state = source
            elif name == "crop":
                box = values.get("box")
                box = (0, 0, *image.size) if box is None else tuple(int(round(v)) for v in box)
                state = _State(result.mode, result.size, ("view", source, box), depth=source.depth + 1)
            elif name == "resize":
                box = values.get("box") or (0, 0, *image.size)
                state = _State(result.mode, result.size, ("view", source, tuple(box)), depth=source.depth + 1)
            elif name == "convert":
                state = _State(result.mode, result.size, ("convert", source, values), depth=source.depth + 1)
            elif name == "filter" and values.get("filter") is ImageFilter.SHARPEN:
                state = source
            else:
                # Other raster filters have no vector equivalent here.
                return
            _assign(result, state)

        _record(result, record)
        return result

    return wrapped


def _paste(image, im, box=None, mask=None):
    if _busy:
        return _PASTE(image, im, box, mask)
    actual_box, actual_mask = box, mask
    if isinstance(actual_box, Image.Image):
        actual_mask, actual_box = actual_box, None
    active = _state(image) is not None or _state(im) is not None or _state(actual_mask) is not None
    prepared = None
    if active:
        try:
            with _native():
                target = _snapshot(image)
                source = _snapshot(im) if isinstance(im, Image.Image) else im
                masking = _snapshot(actual_mask) if actual_mask is not None else None
                region = tuple(actual_box) if actual_box is not None else (0, 0)
                if len(region) == 2:
                    size = im.size if isinstance(im, Image.Image) else actual_mask.size
                    region = (*region, region[0] + size[0], region[1] + size[1])
                prepared = (target, source, region, masking)
        except Exception as error:
            _warning(error)
    with _native():
        result = _PASTE(image, im, box, mask)
    if active:
        if prepared is None:
            _forget(image)
        else:
            def record():
                target, source, region, masking = prepared
                if masking is None and isinstance(source, _State) and region == (0, 0, *image.size) and source.size == image.size:
                    # Renderer.show_image may paste its own canvas; QR frames
                    # repeatedly replace it. Neither operation needs history.
                    if source.mode == image.mode:
                        replacement = source
                    else:
                        replacement = _State(image.mode, image.size, ("convert", source, {"mode": image.mode}), depth=source.depth + 1)
                    _assign(image, replacement)
                    return
                depth = max(target.depth, getattr(source, "depth", 0), getattr(masking, "depth", 0)) + 1
                _assign(image, _State(image.mode, image.size, target.base,
                                     target.ops + (("paste", source, region, masking),), depth))
            _record(image, record)
    return result


def _alpha_composite(first, second):
    if _busy:
        return _ALPHA(first, second)
    with _native():
        result = _ALPHA(first, second)
    if _state(first) is not None or _state(second) is not None:
        def record():
            a, b = _snapshot(first), _snapshot(second)
            _assign(result, _State(result.mode, result.size, ("alpha", a, b), depth=max(a.depth, b.depth) + 1))
        _record(result, record)
    return result


def _invalidate_method(original, draw=False):
    @wraps(original)
    def wrapped(obj, *args, **kwargs):
        if _busy:
            return original(obj, *args, **kwargs)
        with _native():
            result = original(obj, *args, **kwargs)
        _forget(obj._image if draw else obj)
        return result
    return wrapped


def _raster(image, viewport, size):
    x0, y0, x1, y1 = viewport
    if x0 >= 0 and y0 >= 0 and x1 <= image.width and y1 <= image.height:
        return _RESIZE(image, size, Image.Resampling.NEAREST, box=viewport)
    return _TRANSFORM(image, size, Image.Transform.AFFINE,
                      ((x1 - x0) / size[0], 0, x0, 0, (y1 - y0) / size[1], y0),
                      Image.Resampling.NEAREST)


def _scaled_font(font, size):
    key = (font, size)
    if key not in _fonts:
        _fonts[key] = font.font_variant(size=size)
        if len(_fonts) > 32:
            _fonts.popitem(last=False)
    _fonts.move_to_end(key)
    return _fonts[key]


def _mask_image(mask):
    return Image.frombytes("L", mask.size, bytes(mask))


def _text(output, params, viewport, sx, sy):
    xy, text, font = params["xy"], params["text"], params["font"]
    options = {key: params.get(key) for key in ("anchor", "direction", "features", "language")}
    start = tuple(math.modf(c)[0] for c in xy)
    draw = _DRAW(output, params["_mode"])
    fill = params.get("fill")
    stroke = params.get("stroke_width", 0)
    layers = [(stroke, params.get("stroke_fill") if params.get("stroke_fill") is not None else fill)] if stroke else []
    layers.append((0, fill))
    for width, color in layers:
        native, offset = font.getmask2(text, mode=params["_fontmode"], start=start,
                                      stroke_width=width, **options)
        native = _mask_image(native)
        bounds = native.getbbox()
        if bounds is None:
            continue
        left = int(round((int(xy[0]) + offset[0] + bounds[0] - viewport[0]) * sx))
        top = int(round((int(xy[1]) + offset[1] + bounds[1] - viewport[1]) * sy))
        right = int(round((int(xy[0]) + offset[0] + bounds[2] - viewport[0]) * sx))
        bottom = int(round((int(xy[1]) + offset[1] + bounds[3] - viewport[1]) * sy))
        if right <= 0 or bottom <= 0 or left >= output.width or top >= output.height or right <= left or bottom <= top:
            continue
        factor = max(sx, sy)
        high_font = _scaled_font(font, max(1, int(round(font.size * factor))))
        high_width = max(0, int(round(width * factor)))
        high_bounds = high_font.getbbox(text, stroke_width=high_width, **options)
        if max((high_bounds[2] - high_bounds[0]) * (high_bounds[3] - high_bounds[1]),
               (right - left) * (bottom - top)) > _MAX_GLYPH_PIXELS:
            # Exceptionally long labels must not consume unbounded WASM memory.
            ink = _CROP(native, bounds)
            resample = Image.Resampling.NEAREST
        else:
            high, _ = high_font.getmask2(text, mode="L", stroke_width=high_width, **options)
            high = _mask_image(high)
            high_ink = high.getbbox()
            if high_ink is None:
                continue
            ink = _CROP(high, high_ink)
            resample = Image.Resampling.LANCZOS
        if resample == Image.Resampling.NEAREST:
            # Exceptionally long labels allocate only the visible output.
            visible = (max(0, left), max(0, top), min(output.width, right), min(output.height, bottom))
            fx, fy = ink.width / (right - left), ink.height / (bottom - top)
            source_box = ((visible[0] - left) * fx, (visible[1] - top) * fy,
                          (visible[2] - left) * fx, (visible[3] - top) * fy)
            ink = _RESIZE(ink, (visible[2] - visible[0], visible[3] - visible[1]), resample, box=source_box)
            draw.bitmap(visible[:2], ink, fill=color)
        else:
            # Keep one sampling grid for normal text, so scrolling a crop
            # cannot change glyph edge intensities through rounding differences.
            ink = _RESIZE(ink, (right - left, bottom - top), resample)
            draw.bitmap((left, top), ink, fill=color)


def _shape(output, name, params, viewport, sx, sy):
    values = {key: value for key, value in params.items() if not key.startswith("_")}
    coordinates = values["xy"]
    if name == "line":
        # A native line runs through pixel centers, including its endpoints.
        values["xy"] = tuple((int(v) + 0.5 - viewport[i % 2]) * (sx if i % 2 == 0 else sy) - 0.5
                             for i, v in enumerate(coordinates))
    else:
        x0, y0, x1, y1 = coordinates
        values["xy"] = ((int(x0) - viewport[0]) * sx, (int(y0) - viewport[1]) * sy,
                        (int(x1) + 1 - viewport[0]) * sx - 1, (int(y1) + 1 - viewport[1]) * sy - 1)
    if "width" in values:
        width = values["width"]
        values["width"] = max(1, int(round(max(1, width) * min(sx, sy)))) if name == "line" or width else 0
    if "radius" in values:
        values["radius"] *= min(sx, sy)
    getattr(_DRAW(output, params["_mode"]), name)(**values)


def _paste_view(output, source, region, masking, viewport, sx, sy):
    x0, y0, x1, y1 = region
    left = max(0, int(round((x0 - viewport[0]) * sx)))
    top = max(0, int(round((y0 - viewport[1]) * sy)))
    right = min(output.width, int(round((x1 - viewport[0]) * sx)))
    bottom = min(output.height, int(round((y1 - viewport[1]) * sy)))
    if right <= left or bottom <= top:
        return
    box = (left / sx + viewport[0] - x0, top / sy + viewport[1] - y0,
           right / sx + viewport[0] - x0, bottom / sy + viewport[1] - y0)
    size = (right - left, bottom - top)
    image = _paint(source, box, size) if isinstance(source, _State) else source
    mask = _paint(masking, box, size) if masking is not None else None
    _PASTE(output, image, (left, top, right, bottom), mask)


def _paint(state, viewport, size):
    kind, *args = state.base
    if kind == "raster":
        output = _raster(args[0], viewport, size)
    elif kind == "solid":
        output = _NEW(state.mode, size, args[0])
    elif kind == "view":
        source, box = args
        fx = (box[2] - box[0]) / state.size[0]
        fy = (box[3] - box[1]) / state.size[1]
        mapped = (box[0] + viewport[0] * fx, box[1] + viewport[1] * fy,
                  box[0] + viewport[2] * fx, box[1] + viewport[3] * fy)
        output = _paint(source, mapped, size)
    elif kind == "convert":
        source, values = args
        output = _CONVERT(_paint(source, viewport, size), **values)
    elif kind == "alpha":
        output = _ALPHA(_paint(args[0], viewport, size), _paint(args[1], viewport, size))
    else:
        raise ValueError("unknown HD composition")
    sx, sy = size[0] / (viewport[2] - viewport[0]), size[1] / (viewport[3] - viewport[1])
    for op in state.ops:
        if op[0] == "draw":
            _, name, params = op
            if name == "text":
                _text(output, params, viewport, sx, sy)
            else:
                _shape(output, name, params, viewport, sx, sy)
        else:
            _paste_view(output, *op[1:], viewport, sx, sy)
    # Draw operations were clipped to their original image when Pillow ran
    # them. A later out-of-bounds crop must retain that zero-filled padding.
    valid_left = max(0, min(size[0], int(round(-viewport[0] * sx))))
    valid_top = max(0, min(size[1], int(round(-viewport[1] * sy))))
    valid_right = max(0, min(size[0], int(round((state.size[0] - viewport[0]) * sx))))
    valid_bottom = max(0, min(size[1], int(round((state.size[1] - viewport[1]) * sy))))
    for box in ((0, 0, valid_left, size[1]), (valid_right, 0, size[0], size[1]),
                (0, 0, size[0], valid_top), (0, valid_bottom, size[0], size[1])):
        if box[2] > box[0] and box[3] > box[1]:
            _PASTE(output, 0, box)
    return output


def install(scale=8):
    """Enable recording. Repeated calls update output scale without repatching."""
    global _installed, _scale
    if isinstance(scale, bool) or not isinstance(scale, int) or not 1 <= scale <= 8:
        raise ValueError("HD scale must be an integer from 1 to 8")
    _scale = scale
    if _installed:
        return
    ImageDraw.Draw = _draw_factory
    for name in ("text", "rectangle", "rounded_rectangle", "line", "ellipse", "arc"):
        setattr(ImageDraw.ImageDraw, name, _draw_method(name, getattr(ImageDraw.ImageDraw, name)))
    for name in ("copy", "crop", "resize", "convert", "filter"):
        setattr(Image.Image, name, _derived_method(name, getattr(Image.Image, name)))
    Image.Image.paste = _paste
    Image.alpha_composite = _alpha_composite
    for name in ("putpixel", "putdata", "putalpha", "putpalette", "frombytes", "thumbnail", "alpha_composite"):
        setattr(Image.Image, name, _invalidate_method(getattr(Image.Image, name)))
    for name in ("bitmap", "polygon", "pieslice", "chord", "point", "regular_polygon", "shape", "multiline_text"):
        setattr(ImageDraw.ImageDraw, name, _invalidate_method(getattr(ImageDraw.ImageDraw, name), draw=True))
    _installed = True


def render(image):
    """Return display pixels; never mutate the native image or its metrics.

    Unsupported drawing falls back to the complete current native image. A
    sidecar is advisory and must never prevent the wallet from showing a frame.
    """
    size = (image.width * _scale, image.height * _scale)
    with _native():
        if _scale == 1:
            return _COPY(image)
        state = _state(image)
        if state is not None and image.width and image.height:
            try:
                return _paint(state, (0, 0, *image.size), size)
            except Exception as error:
                _warning(error)
        return _RESIZE(image, size, Image.Resampling.NEAREST)
