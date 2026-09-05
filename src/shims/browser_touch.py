"""Mobile touch navigation for the browser, using native screen geometry.

Only selection/focus changes here. The screen's own input loop still handles
activation, validation and navigation. No labels or wallet data leave Python.
"""

from seedsigner.gui.screens.screen import (
    ButtonListScreen, KeyboardScreen, LargeButtonScreen, QRDisplayScreen,
)

TOUCH = 1 << 30
_screen = None
_epoch = 0
_publish = None


def install(publish):
    global _publish
    _publish = publish


def _advance():
    global _epoch
    _epoch = (_epoch + 1) & 4095
    _publish(_epoch)


def enter(screen):
    global _screen
    previous = _screen
    _screen = screen
    _advance()
    return previous


def leave(previous):
    global _screen
    _screen = previous
    _advance()


def _inside(component, x, y):
    left = component.screen_x
    top = component.screen_y - getattr(component, "scroll_y", 0)
    return left <= x < left + component.width and top <= y < top + component.height


def _focus(screen, index):
    nav = getattr(screen, "top_nav", None)
    if nav is not None:
        nav.is_selected = index is None
    for i, button in enumerate(getattr(screen, "buttons", ())):
        button.is_selected = i == index
    if index is not None:
        screen.selected_button = index


def resolve(encoded):
    """Decode one atomic input into an existing button channel, or ignore it.

    The epoch belongs to the displayed screen, so a tap queued during a view
    transition cannot activate a control on the next screen.
    """
    if not encoded & TOUCH:
        return encoded
    screen = _screen
    if screen is None or ((encoded >> 18) & 4095) != _epoch:
        return 0
    x, y = encoded & 511, (encoded >> 9) & 511
    if y == 511 and 1 <= x <= 4:
        return x  # Swipe direction, with the same stale-screen protection.
    if x >= screen.canvas_width or y >= screen.canvas_height:
        return 0

    nav = getattr(screen, "top_nav", None)
    if nav is not None:
        for visible, name in ((nav.show_back_button, "left_button"),
                              (nav.show_power_button and not nav.show_back_button, "right_button")):
            button = getattr(nav, name, None)
            if visible and button is not None and _inside(button, x, y):
                _focus(screen, None)
                return 5

    if isinstance(screen, (ButtonListScreen, LargeButtonScreen)):
        scrolling = getattr(screen, "has_scroll_arrows", False)
        top = screen.top_nav_height if scrolling else nav.height
        bottom = screen.down_arrow_img_y if scrolling else screen.canvas_height
        for i, button in enumerate(screen.buttons):
            button_y = button.screen_y - getattr(button, "scroll_y", 0)
            if scrolling and not top <= button_y < bottom:
                continue
            if y >= top and _inside(button, x, y):
                _focus(screen, i)
                return 5
        if scrolling and abs(x - screen.canvas_width / 2) < 24:
            if y >= screen.down_arrow_img_y:
                return 2
            if screen.up_arrow_img_y <= y < top:
                return 1

    if isinstance(screen, KeyboardScreen):
        save = getattr(screen, "save_button", None)
        if getattr(screen, "show_save_button", False) and save is not None and _inside(save, x, y):
            return 8
        keyboard = screen.keyboard
        for row in keyboard.keys:
            for key in row:
                if not key.is_active:
                    continue
                if (key.screen_x <= x < key.screen_x + keyboard.key_width * key.size
                        and key.screen_y <= y < key.screen_y + keyboard.key_height):
                    old = keyboard.get_selected_key()
                    old.is_selected = False
                    old.render_key()
                    keyboard.selected_key = {"x": key.index_x, "y": key.index_y}
                    key.is_selected = True
                    key.render_key()
                    nav.is_selected = False
                    nav.render_buttons()
                    return 5

    if isinstance(screen, QRDisplayScreen):
        return 5
    return 0
