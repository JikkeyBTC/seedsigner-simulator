"""Direct simulator entry and JikKey identity in both page languages."""

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
        check("entry immediately contains the device", page.locator("#device").count() == 1)
        check("entry title includes JikKey and both firmware names",
              page.title() == "직키 JikKey | 시드사이너·쉴드사이너 시뮬레이터", page.title())
        check("entry shows the supplied logo",
              page.locator("header img.brand-logo[alt='JikKey']").count() == 1)
        check("entry has searchable description", page.locator("#simulator-description").count() == 1)

        page.goto(f"{harness.BASE_URL}/wallet.html?firmware=stock&lang=en",
                  wait_until="domcontentloaded")
        check("English simulator title includes both firmware names",
              page.title() == "JikKey | SeedSigner & ShieldSigner Simulator", page.title())
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
