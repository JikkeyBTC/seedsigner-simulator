"""Real QR decoders must read the entire device at either output density."""
import unittest
from playwright.sync_api import sync_playwright
import harness


class HDQRTests(unittest.TestCase):
    def test_wallet_and_tutorial_read_full_native_or_hd_qr(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for tutorial in (False, True):
                context = browser.new_context(service_workers='block')
                context.add_init_script('window.Worker = class { postMessage() {} terminate() {} };')
                context.route('https://signet.bitsaga.be/**', lambda route: route.fulfill(
                    content_type='application/json', body='{}'))
                page = context.new_page()
                page.goto(harness.wallet_url(**({'tutorial': '1'} if tutorial else {})))
                if not tutorial:
                    page.locator('#wallet-button').click()
                page.wait_for_function('typeof jsQR === "function"')
                for scale in (1, 8):
                    with self.subTest(tutorial=tutorial, scale=scale):
                        result = page.evaluate('''({tutorial, scale}) => {
                            const screen = document.getElementById('screen');
                            screen.width = screen.height = 240 * scale;
                            const ctx = screen.getContext('2d');
                            ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, screen.width, screen.height);
                            ctx.fillStyle = '#000';
                            const matrix = QREncode.matrix('jikkey-hd-qr');
                            const module = Math.floor(208 / matrix.length);
                            const offset = Math.floor((240 - matrix.length * module) / 2);
                            matrix.forEach((row, y) => row.forEach((dark, x) => {
                                if (dark) ctx.fillRect((offset+x*module)*scale,
                                    (offset+y*module)*scale, module*scale, module*scale);
                            }));
                            const app = tutorial ? WalletTutorial.current : WalletCoordinator.current;
                            const result = {read: app.readDevice()};
                            if (tutorial) {
                                app.mirrorDevice();
                                const frame = app.painter.getImageData(0, 0, 640, 480);
                                result.mirror = jsQR(frame.data, 640, 480)?.data;
                            }
                            return result;
                        }''', {'tutorial': tutorial, 'scale': scale})
                        self.assertEqual(result.get('read'), 'jikkey-hd-qr')
                        if tutorial:
                            self.assertEqual(result.get('mirror'), 'jikkey-hd-qr')
                context.close()
            browser.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
