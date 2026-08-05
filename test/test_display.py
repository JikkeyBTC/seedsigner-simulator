"""Both firmware variants boot with the native square JikKey display."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness
from harness import check, report

from playwright.sync_api import sync_playwright


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for firmware in ("smartcard", "stock"):
            page = browser.new_page()
            log = harness.Log(page)
            page.goto(harness.wallet_url(firmware=firmware))
            log.wait(r"display\(\) enter: MainMenuScreen", 240,
                     f"{firmware} firmware to boot")
            dimensions = page.locator("#screen").evaluate(
                "canvas => [canvas.width, canvas.height]")
            check(f"{firmware} boots its 240 by 240 renderer",
                  dimensions == [240, 240], str(dimensions))
            check(f"{firmware} reports a square slot",
                  abs(page.locator("#device .ssd-screen-slot").evaluate(
                      "node => node.getBoundingClientRect().width / node.getBoundingClientRect().height") - 1) < 0.02)
            page.close()
        browser.close()
    return report()


if __name__ == "__main__":
    sys.exit(main())
