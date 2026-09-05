"""Website i18n cannot change firmware content, settings, or navigation."""
import os
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright
import harness


class FirmwareLocaleTests(unittest.TestCase):
    def test_web_language_leaves_both_firmware_screens_untouched(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for firmware in ('smartcard', 'stock'):
                with self.subTest(firmware=firmware):
                    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block')
                    context.add_init_script('''
                        window.workerCount = 0; window.workerMessages = [];
                        const OriginalWorker = window.Worker;
                        window.Worker = class extends OriginalWorker {
                            constructor(...args) { super(...args); window.workerCount++; }
                            postMessage(...args) { workerMessages.push(args[0].type); super.postMessage(...args); }
                        };
                    ''')
                    page = context.new_page()
                    log = harness.Log(page)
                    page.goto(harness.wallet_url(firmware=firmware, lang='ko'))
                    log.wait(r'display\(\) enter: MainMenuScreen', 240, 'the firmware home screen')
                    page.wait_for_timeout(300)
                    self.assertEqual(page.evaluate('JikKeyI18n.language'), 'ko')
                    page.keyboard.press('ArrowRight')  # keep Seeds selected through both switches
                    page.wait_for_timeout(250)
                    original = page.locator('#screen').evaluate('c => c.toDataURL()')
                    workers = page.evaluate('workerCount')
                    messages = page.evaluate('workerMessages.slice()')
                    for language in ('en', 'ko'):
                        page.locator(f'[data-language="{language}"]').click()
                        page.wait_for_function('lang => JikKeyI18n.language === lang', arg=language)
                        page.wait_for_timeout(250)
                        self.assertEqual(log.last_screen(), 'MainMenuScreen')
                        self.assertEqual(page.evaluate('workerCount'), workers)
                        self.assertEqual(page.evaluate('workerMessages'), messages)
                        self.assertEqual(page.locator('#screen').evaluate('c => c.toDataURL()'), original)
                    page.screenshot(path=harness.artifact(f'web-ko-firmware-{firmware}.png'), full_page=True)
                    page.locator('[data-language="ko"]').evaluate('b => b.blur()')
                    page.keyboard.press('Enter')
                    log.wait(r'display\(\) exit: MainMenuScreen -> 1', 15, 'the same selected menu item')
                    self.assertFalse(any('RAISED' in line for line in log.lines), '\n'.join(log.lines[-12:]))
                    context.close()
            browser.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
