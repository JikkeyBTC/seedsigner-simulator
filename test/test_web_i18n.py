"""Live page language, dynamic companion states and an intact in-progress form.

No firmware boot or faucet is needed for these UI assertions. The actual page,
tray and coordinator renderers run unchanged; only their external inputs are
supplied by the test. Run against the existing test server on SIM_PORT (8770).
"""
import os
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE = os.environ.get("SIM_URL", "http://127.0.0.1:" + os.environ.get("SIM_PORT", "8770")).rstrip("/")
ARTIFACTS = Path(__file__).resolve().parents[1] / "test" / "artifacts" / "web-i18n"


class WebLanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()
        ARTIFACTS.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 1000}, service_workers="block")
        self.context.add_init_script("window.Worker = class { postMessage(message) { if(message.type === 'init') window.testWalletInit = message; } terminate() {} };")
        self.context.route("https://signet.bitsaga.be/**", lambda route: route.fulfill(
            status=200, content_type="application/json", body='{"faucet_ready":true,"payout_sat":100000,"addresses":{}}'))
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def open(self, params="firmware=smartcard"):
        self.page.goto(BASE + "/wallet.html?" + params)
        self.page.wait_for_function("window.JikKeyI18n && document.querySelector('#wallet-button, #tutorial')")

    def choose(self, language):
        self.page.locator('[data-language="' + language + '"]').click()
        self.page.wait_for_function("language => document.documentElement.lang === language", arg=language)

    def has_text(self, selector, expected):
        self.page.wait_for_function("([selector, expected]) => document.querySelector(selector).textContent.includes(expected)", arg=[selector, expected])

    def test_default_switch_persistence_and_dynamic_card_state(self):
        self.open()
        self.assertEqual(self.page.evaluate("JikKeyI18n.language"), "ko")
        self.has_text("#warning", "실제 자산")
        self.has_text("#wallet-button", "연습 지갑 열기")
        self.page.evaluate("window.languageEvents=[]; addEventListener('jikkey-language-change', e => languageEvents.push(e.detail.language))")
        self.page.locator('.cardtray-card[data-index="0"]').click()
        self.has_text(".cardtray-slotlabel", "카드 A 연결됨")
        self.page.evaluate("CardTray.forWorker(testWalletInit.cardBuffer).publish(0, 0, 1 | (2 << 8))")
        self.has_text(".cardtray-tries", "2번 남음")
        self.choose("en")
        self.has_text(".cardtray-slotlabel", "Card A inserted")
        self.has_text(".cardtray-tries", "2 PIN tries left")
        self.has_text("#warning", "Never enter")
        self.choose("ko")
        self.page.locator(".cardtray-eject").click()
        self.has_text(".cardtray-slotlabel", "카드를 넣어 주세요")
        self.assertEqual(self.page.evaluate("languageEvents"), ["en", "ko"])
        self.assertEqual(self.page.evaluate("localStorage.getItem('jikkey.language')"), "ko")
        self.assertTrue(self.page.evaluate("Object.getOwnPropertyDescriptor(JikKeyI18n, 'language').set === undefined"))
        self.assertEqual(self.page.evaluate("JikKeyI18n.t('Address {index}', {index: 4})"), "Address 4")
        self.page.reload()
        self.has_text("#wallet-button", "연습 지갑 열기")
        self.choose("en")
        self.page.reload()
        self.has_text("#wallet-button", "Open wallet")

    def test_query_precedence_invalid_values_and_keyboard_switch(self):
        self.open("firmware=stock&lang=en")
        self.assertEqual(self.page.evaluate("JikKeyI18n.language"), "en")
        self.page.locator('[data-language="ko"]').focus()
        self.page.keyboard.press("Enter")
        self.has_text("#wallet-button", "연습 지갑 열기")
        self.assertIn("lang=ko", self.page.url)
        self.page.evaluate("localStorage.setItem('jikkey.language', 'en')")
        self.open("firmware=stock&lang=ko")
        self.assertEqual(self.page.evaluate("JikKeyI18n.language"), "ko")
        self.open("firmware=stock&lang=invalid")
        self.assertEqual(self.page.evaluate("JikKeyI18n.language"), "en")
        self.page.evaluate("localStorage.setItem('jikkey.language', 'invalid')")
        self.open("firmware=stock&lang=invalid")
        self.assertEqual(self.page.evaluate("JikKeyI18n.language"), "ko")

    def test_wallet_form_switch_preserves_address_amount_and_state(self):
        self.open()
        self.page.locator("#wallet-button").click()
        self.has_text(".wal-howto", "연습용 시드")
        # Render a real send form from deterministic public wallet data.
        self.page.evaluate("""() => {
          const wallet = WalletCoordinator.current;
          wallet.reader++;
          wallet.stage = 'ready'; wallet.view = 'send';
          wallet.records = [{address:'tb1qexample', branch:0, index:0}];
          wallet.chain = {tb1qexample:{confirmed:200000, unconfirmed:0, utxos:[], history:[]}};
          wallet.render();
          window.keptInput = document.getElementById('wal-to');
          keptInput.setAttribute('placeholder', 'To');
          keptInput.setAttribute('aria-label', 'To');
        }""")
        address = "tb1qdonttranslate123456789"
        self.page.locator("#wal-to").fill(address)
        self.page.locator("#wal-amount").fill("12345")
        self.choose("en")
        self.assertEqual(self.page.locator("#wal-to").input_value(), address)
        self.assertEqual(self.page.locator("#wal-to").get_attribute("placeholder"), "To")
        self.assertEqual(self.page.locator("#wal-amount").input_value(), "12345")
        self.assertTrue(self.page.evaluate("keptInput === document.getElementById('wal-to')"))
        self.assertEqual(self.page.evaluate("WalletCoordinator.current.view"), "send")
        self.has_text(".wal-actions", "Create transaction")
        self.choose("ko")
        self.assertEqual(self.page.locator("#wal-to").get_attribute("placeholder"), "받는 주소")
        self.assertEqual(self.page.locator("#wal-to").get_attribute("aria-label"), "받는 주소")
        self.has_text(".wal-actions", "거래 만들기")
        self.page.evaluate("WalletCoordinator.current.say('Code 3 of 7.')")
        self.has_text(".wal-say[aria-live]", "7개 중 3개")
        self.page.screenshot(path=str(ARTIFACTS / "wallet-ko.png"), full_page=True)

    def test_tutorial_dynamic_prose_and_seed_data_are_reversible(self):
        self.open("firmware=smartcard&tutorial=1")
        self.has_text(".tut-step", "준비됐어요")
        seed = self.page.evaluate("WalletTutorial.seeds[0].words")
        self.assertIn(seed, self.page.locator(".tut-fold").text_content())
        self.page.evaluate("WalletTutorial.current.transfer('in', 'The twelve word test seed for Card A, as a SeedQR.')")
        self.has_text(".tut-caption", "카드 A")
        self.has_text(".tut-arrow", "연습 지갑 → 기기")
        self.choose("en")
        self.has_text(".tut-caption", "The twelve word test seed for Card A")
        self.has_text(".tut-arrow", "Phone")
        self.assertIn(seed, self.page.locator(".tut-fold").text_content())
        self.choose("ko")
        self.page.evaluate("WalletTutorial.current.fail(new Error('Bitsaga Signet did not answer in time'))")
        self.has_text(".tut-verdict", "응답이 늦어지고")
        self.has_text(".tut-do", "다시 시도")
        self.page.screenshot(path=str(ARTIFACTS / "tutorial-ko.png"), full_page=True)

    def test_every_tutorial_step_and_action_has_korean_copy(self):
        self.open("firmware=smartcard&tutorial=1")
        untranslated = self.page.evaluate("""() => {
          const tutorial = WalletTutorial.current;
          tutorial.gate = () => new Promise(() => {});
          tutorial.run(0);
          const copy = tutorial.steps.flatMap(step => [step.title, step.text,
            ...step.actions.map(action => action.instruct)]).filter(Boolean);
          return copy.filter(source => !/[가-힣]/.test(JikKeyI18n.t(source)));
        }""")
        self.assertEqual(untranslated, [])

    def test_korean_instructions_keep_native_english_device_menu_labels(self):
        self.open("firmware=smartcard&tutorial=1")
        missing = self.page.evaluate("""() => {
          const tutorial = WalletTutorial.current;
          tutorial.gate = () => new Promise(() => {});
          tutorial.run(0);
          const actions = tutorial.steps.flatMap(step => step.actions.map(action => action.instruct)).filter(Boolean);
          const copy = actions.concat([
            'Tools → New seed',
            'Seeds → your seed → Export Xpub → Single sig → Native Segwit',
            'On the device, go to Scan.',
            'On the device, go to Scan',
            'The camera was refused, so scanning will not work. Everything else will. Allow it in the address bar and press Scan again.',
            'Something else on this machine is holding the camera, so scanning will not work. Close it and press Scan again.'
          ]);
          const labels = ['Tools', 'New seed', 'Seeds', 'Export Xpub', 'Single sig',
            'Native Segwit', 'Scan', 'Backup seed', 'To SeedKeeper', 'Discard',
            'From SeedKeeper', 'Multisig', 'Static', 'Done'];
          return copy.flatMap(source => labels.filter(label => source.includes(label)
            && !JikKeyI18n.t(source).includes(label)).map(label => ({source, label})));
        }""")
        self.assertEqual(missing, [])

    def test_escape_dismisses_fullscreen_and_about_from_language_switch(self):
        self.open("firmware=stock")
        self.page.set_viewport_size({"width": 844, "height": 390})
        self.page.locator("#fullscreen").click()
        self.page.locator('[data-language="ko"]').focus()
        self.page.keyboard.press("Escape")
        self.assertFalse(self.page.evaluate("document.body.classList.contains('solo')"))
        self.assertEqual(self.page.locator("#fullscreen").get_attribute("aria-pressed"), "false")
        self.page.locator("#about > summary").click()
        self.assertTrue(self.page.locator("#about").evaluate("node => node.open"))
        # Programmatic focus avoids the ordinary outside-pointer dismissal.
        self.page.locator('[data-language="en"]').focus()
        self.page.keyboard.press("Escape")
        self.assertFalse(self.page.locator("#about").evaluate("node => node.open"))

    def test_responsive_logo_switch_and_suede_fullscreen(self):
        self.open("firmware=stock")
        for width, height, label in [(1440,1000,"desktop"),(390,844,"phone"),(844,390,"landscape")]:
            self.page.set_viewport_size({"width":width,"height":height})
            self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
            self.assertTrue(self.page.evaluate("""() => {
              const a=document.querySelector('.brand-title').getBoundingClientRect();
              const b=document.querySelector('#language-switch').getBoundingClientRect();
              return a.right < b.left;
            }"""))
            self.assertTrue(self.page.evaluate("document.querySelector('.brand-logo').naturalWidth === 251"))
            self.page.screenshot(path=str(ARTIFACTS / (label + "-ko.png")), full_page=True)
        self.page.locator("#fullscreen").click()
        self.has_text("#fullscreen-label", "원래 화면")
        self.assertIn("jikkey-suede.svg", self.page.evaluate("getComputedStyle(document.body, '::before').backgroundImage"))
        self.choose("en")
        self.has_text("#fullscreen-label", "Back to the page")
        self.page.screenshot(path=str(ARTIFACTS / "fullscreen-en.png"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
