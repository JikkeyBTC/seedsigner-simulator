"""JikKey identity on the landing page and simulator chrome."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness
from harness import check, report

from playwright.sync_api import sync_playwright


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(service_workers="block").new_page()

        page.goto(f"{harness.BASE_URL}/index.html", wait_until="domcontentloaded")
        check("landing title is JikKey", page.title() == "JikKey Simulator", page.title())
        check("landing shows the supplied logo",
              page.locator("img.brand-logo[alt='JikKey']").count() == 1)
        check("landing accent is JikKey Blue",
              page.evaluate(
                  "getComputedStyle(document.documentElement)"
                  ".getPropertyValue('--accent').trim().toLowerCase()") == "#0076ff")

        page.goto(f"{harness.BASE_URL}/wallet.html?firmware=stock",
                  wait_until="domcontentloaded")
        check("simulator title is JikKey", page.title() == "JikKey Simulator", page.title())
        check("simulator shows the supplied logo",
              page.locator("header img.brand-logo[alt='JikKey']").count() == 1)
        switch = page.locator("#firmware-switch").inner_text()
        check("firmware names remain accurate",
              "SeedSigner" in switch and "ShieldSigner" in switch, switch)
        logo = page.locator("img.brand-logo")
        check("logo is local and loaded",
              logo.count() == 1 and logo.evaluate(
                  "img => img.complete && img.naturalWidth > 0"))
        browser.close()
    return report()


if __name__ == "__main__":
    sys.exit(main())
