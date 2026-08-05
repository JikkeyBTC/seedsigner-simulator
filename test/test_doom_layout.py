"""The boot game paints native square frames and keeps its unlock sequence."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness
from harness import check, report

from playwright.sync_api import sync_playwright


STUB = """
window.__doom = {frames: [], unlocked: 0};
window.DoomRun = {
  ready: Promise.resolve(),
  start(options) { window.__doom.onFrame = options.onFrame; },
  key() {},
  stop() { window.__doom.stopped = true; }
};
"""


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(service_workers="block").new_page()
        page.evaluate(STUB)
        page.add_script_tag(path=os.path.join(
            harness.REPO, "src", "web", "doom-boot.js"))
        state = page.evaluate("""async () => {
          DoomBoot.boot({
            width: 240, height: 240,
            paint(bytes) { window.__doom.frames.push(bytes.length); },
            status() {},
            onUnlock() { window.__doom.unlocked++; },
            onUnavailable(reason) { window.__doom.unavailable = reason; }
          });
          await Promise.resolve();
          window.__doom.onFrame(new Uint8Array(240 * 240 * 2));
          DoomBoot.key(6); DoomBoot.key(7); DoomBoot.key(8);
          return window.__doom;
        }""")
        check("DOOM paints one square RGB frame", state["frames"] == [240 * 240 * 3], str(state))
        check("side buttons still unlock the wallet", state["unlocked"] == 1, str(state))
        check("unlock stops DOOM", state.get("stopped") is True, str(state))
        browser.close()
    return report()


if __name__ == "__main__":
    sys.exit(main())
