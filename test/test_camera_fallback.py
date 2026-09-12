"""Exercise the camera channel with incomplete native BarcodeDetector support.

Only public synthetic entropy is used. Camera frames pass through the real
canvas, jsQR decoder and shared buffer; no firmware or physical camera is needed.
"""
import os
import unittest
from playwright.sync_api import sync_playwright

BASE = os.environ.get('SIM_URL', 'http://127.0.0.1:' + os.environ.get('SIM_PORT', '8770')).rstrip('/')
PAYLOAD = [0, 255, 128, 233, 1, 2, 3, 4, 9, 10, 13, 127, 240, 159, 146, 165]


class CameraFallbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(service_workers='block')
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.route('**/__camera_fallback_test.html', lambda route: route.fulfill(
            status=200,
            headers={'Content-Type': 'text/html', 'Cross-Origin-Opener-Policy': 'same-origin',
                     'Cross-Origin-Embedder-Policy': 'require-corp'},
            body='<html><head></head><body></body></html>'))
        self.page.goto(BASE + '/__camera_fallback_test.html')
        for script in ('wallet-camera.js', 'qr-encode.js', 'jsQR.js'):
            self.page.add_script_tag(url=BASE + '/' + script)

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def start_camera(self, mode, blank=False):
        self.page.evaluate("""({mode, blank, payload}) => {
          window.nativeCalls = 0;
          if (mode === 'absent') {
            delete window.BarcodeDetector;
          } else {
            window.BarcodeDetector = class {
              static getSupportedFormats() { return Promise.resolve(['qr_code']); }
              detect() {
                window.nativeCalls++;
                if (mode === 'throw') throw new Error('Not implemented');
                if (mode === 'reject') return Promise.reject(new DOMException('Not implemented', 'NotSupportedError'));
                if (mode === 'hang') return new Promise(() => {});
                if (mode === 'empty') return Promise.resolve([]);
                return Promise.resolve([{rawValue: '\\uFFFD\\uFFFD\\uFFFDnot the seed\\uFFFD', format:'qr_code'}]);
              }
            };
          }
          const canvas = document.createElement('canvas');
          canvas.width = 640; canvas.height = 480;
          const ctx = canvas.getContext('2d');
          const modules = QREncode.matrix(payload);
          const draw = () => {
            ctx.fillStyle='white'; ctx.fillRect(0,0,640,480);
            if (blank) return;
            ctx.fillStyle='black';
            const size=10, x=(640-modules.length*size)/2, y=(480-modules.length*size)/2;
            modules.forEach((row,r) => row.forEach((value,c) => {
              if(value) ctx.fillRect(x+c*size,y+r*size,size,size);
            }));
          };
          draw(); setInterval(draw,66);
          window.cameraBuffer = CameraChannel.createBuffer();
          window.cameraHeader = new Int32Array(cameraBuffer,0,16);
          window.trouble = '';
          window.camera = CameraChannel.runPage(cameraBuffer, {
            source: () => canvas.captureStream(15),
            onTrouble: value => window.trouble=value,
          });
          Atomics.store(cameraHeader,0,1);
        }""", {'mode': mode, 'blank': blank, 'payload': PAYLOAD})

    def expect_exact_payload(self, mode):
        self.start_camera(mode)
        self.page.wait_for_function('Atomics.load(cameraHeader,5)>0 || Atomics.load(cameraHeader,1)===3', timeout=3500)
        self.assertEqual(self.page.evaluate('Atomics.load(cameraHeader,1)'), 2, 'camera must remain running')
        received=self.page.evaluate('Array.from(CameraChannel.forWorker(cameraBuffer).payload())')
        self.assertEqual(received, PAYLOAD, 'raw binary entropy must survive unchanged')
        if mode != 'absent':
            self.assertGreater(self.page.evaluate('nativeCalls'), 0)
        if mode in ('throw', 'reject', 'hang'):
            self.page.wait_for_timeout(150)
            self.assertEqual(self.page.evaluate('nativeCalls'), 1, 'failed detector must stay disabled')

    def test_no_native_api(self):
        self.expect_exact_payload('absent')

    def test_native_detection_keeps_binary_bytes(self):
        self.expect_exact_payload('match')

    def test_native_sync_error_falls_back(self):
        self.expect_exact_payload('throw')

    def test_native_rejection_falls_back(self):
        self.expect_exact_payload('reject')

    def test_native_timeout_falls_back(self):
        self.expect_exact_payload('hang')

    def test_native_false_negative_does_not_block_jsqr(self):
        self.expect_exact_payload('empty')

    def test_native_text_cannot_invent_a_seed_from_blank_frames(self):
        self.start_camera('match', blank=True)
        self.page.wait_for_function('Atomics.load(cameraHeader,2)>=8', timeout=3500)
        self.assertEqual(self.page.evaluate('Atomics.load(cameraHeader,5)'), 0)
        self.assertEqual(self.page.evaluate('Atomics.load(cameraHeader,1)'), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
