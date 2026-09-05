"""Both firmwares retain a 240px layout with an eightfold display backing."""

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
            page.wait_for_function("document.querySelector('#screen').width === 1920", timeout=60000)
            dimensions = page.locator("#screen").evaluate(
                "canvas => [canvas.width, canvas.height]")
            check(f"{firmware} emits a 1920 by 1920 frame",
                  dimensions == [1920, 1920], str(dimensions))
            check(f"{firmware} keeps native 240 by 240 layout coordinates",
                  page.locator('#screen').evaluate(
                      "c => [Number(c.dataset.logicalWidth), Number(c.dataset.logicalHeight)]") == [240, 240])
            check(f"{firmware} reports a square slot",
                  abs(page.locator("#device .ssd-screen-slot").evaluate(
                      "node => node.getBoundingClientRect().width / node.getBoundingClientRect().height") - 1) < 0.02)
            page.close()
        browser.close()
    return report()


if __name__ == "__main__":
    sys.exit(main())
