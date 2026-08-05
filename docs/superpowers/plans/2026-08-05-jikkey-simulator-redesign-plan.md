# JikKey Simulator Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebrand the SeedSigner and ShieldSigner simulator as JikKey, boot both firmware variants at 240×240, and replace the current shell with a responsive SVG derived from the supplied STEP cover without changing wallet behavior.

**Architecture:** Keep the existing vanilla HTML/CSS/JavaScript page, Pyodide worker, shared-memory input channels, and one live firmware canvas. Change the simulator-created display setting and initial canvas to 240×240, render that canvas inside a new CAD-derived `SeedSignerDevice` SVG, and apply the locally served JikKey asset and blue palette only to browser-owned chrome. The worker-reported renderer size remains authoritative so an unexpected firmware size degrades by rebuilding the shell instead of blocking.

**Tech Stack:** Vanilla HTML/CSS/JavaScript, SVG, Pyodide Web Worker, Python 3 browser tests, Playwright, existing shell checksum tooling.

## Global Constraints

- Use JikKey Blue `#0076FF` with black and white supporting colors.
- Preserve the colors drawn by SeedSigner and ShieldSigner firmware inside the canvas.
- Preserve all eight input channels: `up`, `down`, `left`, `right`, `select`, `key1`, `key2`, and `key3`.
- The 240×240 display is not a pointer or touch control.
- Preserve camera, QR, smartcard, tutorial, coordinator, firmware switching, fullscreen, CSP, COOP, COEP, Testnet default, and error behavior.
- Preserve SeedSigner and ShieldSigner names when they identify upstream firmware, along with `LICENSE`, `THIRD-PARTY.md`, credits, and non-endorsement language.
- Do not modify upstream firmware inside either wallet zip.
- Do not add a framework, remote font, remote icon, analytics dependency, or new CSP origin.
- Update `build/checksums.txt` in every commit that changes or adds a served file.
- Reference assets are `D:/스마트스토어/Seedsigner_HAT/양산/final/cover.step` and `D:/스마트스토어/seedsigner/상표관련/로고/직키로고/svg/svg_output/logo_7.svg`.

## File structure

- Create `src/web/jikkey-logo.svg`: transparent, tightly cropped web logo derived from the supplied SVG.
- Create `test/test_brand.py`: fast, firmware-free checks for JikKey names, logo, palette, and local asset loading.
- Create `test/test_display.py`: live checks that both firmware variants really render 240×240.
- Create `test/test_doom_layout.py`: fast stubbed-frame check for square DOOM rendering and the side-button unlock.
- Modify `src/web/index.html`: landing-page name, logo, favicon, theme, and accent.
- Modify `src/web/wallet.html`: simulator name/logo, palette variables, 240×240 initial canvas, and square startup dimensions.
- Modify `src/web/manifest.json`: JikKey PWA identity and SVG icon.
- Modify `src/web/sw.js`: cache the JikKey logo and use JikKey cache naming on the next version.
- Modify `src/web/wallet-worker.js`: write `st7789_240x240` into simulator settings.
- Modify `src/web/doom-boot.js`: consume native 240×240 frames without stretching or cropping.
- Modify `src/web/seedsigner-device.js`: CAD-derived shell geometry, five front controls, three side controls, JikKey states, and accessible keyboard activation.
- Modify `src/web/wallet-cards.js`, `src/web/wallet-coordinator.js`, and `src/web/wallet-tutorial.js`: browser-owned JikKey accent styling.
- Modify `test/test_device.py`, `test/test_tray_layout.py`, `test/run.py`, `test/harness.py`, and visual baselines: square geometry and JikKey assertions.
- Modify `README.md`, `docs/ARCHITECTURE.md`, `test/README.md`, and `docs/img/device.png`: 240×240 JikKey documentation.
- Modify `build/checksums.txt`: hashes for every changed or added served file.

---

### Task 1: Install JikKey branding and page identity

**Files:**
- Create: `src/web/jikkey-logo.svg`
- Create: `test/test_brand.py`
- Modify: `src/web/index.html:7-79`
- Modify: `src/web/wallet.html:13-20, 178-190, 438-442`
- Modify: `src/web/manifest.json`
- Modify: `src/web/sw.js:21-64`
- Modify: `test/run.py:45-52`
- Modify: `build/checksums.txt`

**Interfaces:**
- Consumes: supplied `logo_7.svg` geometry and color `#0076FF`.
- Produces: local `jikkey-logo.svg`, `.brand-logo`, `.brand-title`, and root CSS variable `--accent` for later tasks.

- [ ] **Step 1: Write the failing brand test**

Create `test/test_brand.py` with fast page-level checks that do not wait for Python:

```python
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
              page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--accent').trim().lower()")
              == "#0076ff")

        page.goto(f"{harness.BASE_URL}/wallet.html?firmware=stock", wait_until="domcontentloaded")
        check("simulator title is JikKey", page.title() == "JikKey Simulator", page.title())
        check("simulator shows the supplied logo",
              page.locator("header img.brand-logo[alt='JikKey']").count() == 1)
        check("firmware names remain accurate",
              page.locator("#firmware-switch").inner_text().find("SeedSigner") >= 0
              and page.locator("#firmware-switch").inner_text().find("ShieldSigner") >= 0)
        check("logo is local and loaded",
              page.locator("img.brand-logo").evaluate("img => img.complete && img.naturalWidth > 0"))
        browser.close()
    return report()


if __name__ == "__main__":
    sys.exit(main())
```

Add `("brand", ["test_brand.py"], True)` before `tray_layout` in `test/run.py`.

- [ ] **Step 2: Run the brand test and verify it fails**

Run: `python test/run.py brand`

Expected: FAIL because titles still say SeedSigner, `.brand-logo` does not exist, and `--accent` is `#f7931a`.

- [ ] **Step 3: Add the sanitized local logo**

Copy the supplied SVG, then edit the copy with `apply_patch`:

```powershell
Copy-Item -LiteralPath 'D:\스마트스토어\seedsigner\상표관련\로고\직키로고\svg\svg_output\logo_7.svg' `
  -Destination 'src\web\jikkey-logo.svg'
```

Change the root `viewBox` to `18 138 296 58`, remove fixed `width` and `height`, add `role="img" aria-labelledby="jikkey-title"`, insert `<title id="jikkey-title">JikKey</title>`, remove `sodipodi:namedview`, and remove the opaque white background path `id="path10"`. Retain path IDs `path12`, `path14`, `path26`, `path28`, `path32`, `path36`, `path40`, `path44`, `path46`, `path48`, `path50`, `path52`, `path54`, `path56`, `path58`, `path60`, `path62`, `path64`, `path66`, `path68`, `path70`, and `path72` unchanged. Verify the retained paths use only `#000000` and `#0076ff` and that no white rectangle remains.

- [ ] **Step 4: Apply JikKey page identity**

In `index.html`, use the local SVG as favicon and header identity:

```html
<title>JikKey Simulator</title>
<link rel="icon" href="jikkey-logo.svg" type="image/svg+xml">
<h1 class="brand-title">
  <img class="brand-logo" src="jikkey-logo.svg" alt="JikKey">
  <span>Simulator</span>
</h1>
```

Set `--accent: #0076ff`, add `.brand-title` as a flex row, and constrain `.brand-logo` to `width: min(12rem, 58vw); height: auto`.

In `wallet.html`, set `<title>JikKey Simulator</title>`, add the same SVG favicon, define `--accent: #0076ff` in `:root`, and replace the header `<h1>` with the same logo-plus-`Simulator` structure while retaining the adjacent technical-details control.

Change `manifest.json` identity to:

```json
{
  "name": "JikKey Simulator",
  "short_name": "JikKey",
  "description": "SeedSigner and ShieldSigner firmware running in a JikKey browser simulator.",
  "id": "./",
  "start_url": "./index.html",
  "scope": "./",
  "display": "standalone",
  "orientation": "any",
  "background_color": "#0b0c0e",
  "theme_color": "#0076ff",
  "icons": [
    { "src": "jikkey-logo.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any" }
  ]
}
```

Add `./jikkey-logo.svg` to `sw.js` `SHELL`, change the cache prefix to `jikkeysim-`, and increment `VERSION` to `sim-v8` because the old SeedSigner-branded immutable icon set must no longer define the installed app. During activation, delete obsolete caches whose names start with either `jikkeysim-` or the former `seedsignersim-` prefix.

- [ ] **Step 5: Refresh served-file checksums and run the test**

Run:

```bash
bash build/update-checksums.sh
python test/run.py brand
bash build/update-checksums.sh --check
```

Expected: brand test PASS; checksum check PASS.

- [ ] **Step 6: Commit the branding slice**

```bash
git add src/web/jikkey-logo.svg src/web/index.html src/web/wallet.html \
  src/web/manifest.json src/web/sw.js test/test_brand.py test/run.py build/checksums.txt
git commit -m "feat: apply JikKey simulator identity"
```

---

### Task 2: Boot both firmware variants and DOOM at 240×240

**Files:**
- Create: `test/test_display.py`
- Create: `test/test_doom_layout.py`
- Modify: `src/web/wallet-worker.js:170-192`
- Modify: `src/web/wallet.html:584-587, 788-793, 1065-1075`
- Modify: `src/web/doom-boot.js:45-55, 111-137, 181-193`
- Modify: `test/run.py:45-56`
- Modify: `build/checksums.txt`

**Interfaces:**
- Consumes: existing worker `size` message `{type, width, height}` and `DoomBoot.boot(options)` API.
- Produces: initial and live 240×240 canvas; DOOM `onFrame(frame: Uint8Array)` accepting exactly `240 * 240 * 2` RGB565 bytes.

- [ ] **Step 1: Write the failing live firmware display test**

Create `test/test_display.py`:

```python
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
```

Add `("display", ["test_display.py"], True)` after `device` in `test/run.py`.

- [ ] **Step 2: Write the failing stubbed DOOM test**

Create `test/test_doom_layout.py`. Stub `DoomRun` before page scripts execute, feed one native frame, and exercise the real unlock state machine:

```python
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
  stop() { window.__doom.stopped = true; }
};
"""


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(service_workers="block").new_page()
        page.add_init_script(STUB)
        page.goto(f"{harness.BASE_URL}/index.html")
        page.add_script_tag(url=f"{harness.BASE_URL}/doom-boot.js")
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
```

Add `("doom_layout", ["test_doom_layout.py"], True)` after `device` and before live `display`.

- [ ] **Step 3: Run the new tests and verify they fail**

Run:

```bash
python test/run.py doom_layout
python test/run.py display
```

Expected: DOOM test FAIL because `DOOM_W` is 320; live display FAIL because both firmware settings select 320×240.

- [ ] **Step 4: Change the simulator-created firmware setting**

In `wallet-worker.js`, retain Testnet and change only the display setting:

```javascript
json.dump({"display_config": "st7789_240x240", "network": "T"}, handle)
```

Update the adjacent comment to describe the compact square ST7789 configuration.

In `wallet.html`, start square before the worker replies:

```html
<canvas id="screen" width="240" height="240"></canvas>
```

```javascript
let W = 240, H = 240;  // corrected by the worker once the renderer exists
```

Keep `worker.onmessage` resizing and `mountDevice(W, H)` unchanged so the renderer report remains authoritative. Change the `maxWidth` comment to describe responsive shell scaling rather than the old 320×240 ratio.

- [ ] **Step 5: Align DOOM with native square frames**

In `doom-boot.js`, set:

```javascript
var DOOM_W = 240;
var DOOM_H = 240;
```

Retain byte-count validation, RGB565 conversion, and unlock handling. Keep the centering math so a future larger renderer can still display a native square frame, but assert nonnegative offsets before painting:

```javascript
offsetX = (panelW - DOOM_W) >> 1;
offsetY = (panelH - DOOM_H) >> 1;
if (offsetX < 0 || offsetY < 0) {
  unavailable("the device panel is smaller than the 240x240 boot game");
  return;
}
```

Rewrite comments that claim 320×240 and state that the original boot-game port supplies native 240×240 RGB565 frames.

- [ ] **Step 6: Refresh checksums and run square display tests**

```bash
bash build/update-checksums.sh
python test/run.py doom_layout
python test/run.py display
bash build/update-checksums.sh --check
```

Expected: both tests PASS for DOOM, ShieldSigner, and SeedSigner.

- [ ] **Step 7: Commit the display slice**

```bash
git add src/web/wallet-worker.js src/web/wallet.html src/web/doom-boot.js \
  test/test_display.py test/test_doom_layout.py test/run.py build/checksums.txt
git commit -m "feat: boot JikKey simulator at 240x240"
```

---

### Task 3: Replace the shell with the CAD-derived JikKey controls

**Files:**
- Modify: `src/web/seedsigner-device.js:1-670`
- Modify: `test/test_device.py:1-245`
- Modify: `build/checksums.txt`

**Interfaces:**
- Consumes: `SeedSignerDevice.render(container, {screenWidth, screenHeight, interactive, card, onKey, maxWidth})` and existing channel numbers 1–8.
- Produces: the same public `render()` return shape plus `.ssd-screw`, `.ssd-jikkey-mark`, `.ssd-control--front`, and `.ssd-control--side` markers used by tests.

- [ ] **Step 1: Rewrite device expectations before production code**

In `test/test_device.py`, change the probe to `screenWidth: 240, screenHeight: 240`. Add these checks immediately after the probe is mounted:

```python
controls = page.locator("#probe [data-ssd-control]")
check("the JikKey shell exposes all eight controls",
      controls.evaluate_all("nodes => nodes.map(n => n.dataset.ssdControl)")
      == ["up", "down", "left", "right", "select", "key1", "key2", "key3"])
check("five controls are on the front",
      page.locator("#probe .ssd-control--front").count() == 5)
check("three controls are on the side",
      page.locator("#probe .ssd-control--side").count() == 3)
check("the CAD cover keeps four screw holes",
      page.locator("#probe .ssd-screw").count() == 4)
check("the shell carries a JikKey mark",
      page.locator("#probe .ssd-jikkey-mark").count() == 1)
check("every live control has an accessible name and keyboard focus",
      controls.evaluate_all("nodes => nodes.every(n => n.tabIndex === 0 && n.getAttribute('aria-label'))"))
```

Replace both 4:3 assertions with `abs(screen_shape() - 1) < 0.02`. Add a focused-control keyboard check:

```python
page.evaluate("() => { window.__presses.length = 0; }")
page.locator("#probe [data-ssd-control=key1]").focus()
page.keyboard.press("Enter")
page.wait_for_timeout(250)
check("Enter activates the focused side key once", presses(page) == [6], str(presses(page)))
```

Keep the existing tests for screen inertness, one press per touch, held-touch non-repetition, fullscreen fit, Escape, and horizontal overflow.

- [ ] **Step 2: Run the device test and verify it fails**

Run: `python test/run.py device`

Expected: FAIL on CAD markers, side/front classes, square-screen assertions, and keyboard-accessible controls.

- [ ] **Step 3: Replace the layout with STEP-derived proportions**

Keep `CHANNEL`, `render()`, percentage screen positioning, and the public return object. Replace the SeedSigner Plus stadium layout with a 66.0:32.8 cover layout based on tenths of a millimeter:

```javascript
function layout(screenW, screenH, scale) {
  var sw = Math.round(screenW * scale);
  var sh = Math.round(screenH * scale);
  var u = sh / 240;
  var L = {u: u, sw: sw, sh: sh};
  L.bodyX = 22 * u;
  L.bodyY = 18 * u;
  L.bodyW = Math.max(660 * u, sw + 420 * u);
  L.bodyH = 328 * u;
  L.screenX = L.bodyX + (L.bodyW - sw) / 2;
  L.screenY = L.bodyY + (L.bodyH - sh) / 2;
  L.sideReach = 24 * u;
  L.viewW = L.bodyW + L.bodyX * 2 + L.sideReach;
  L.viewH = L.bodyH + L.bodyY * 2;
  L.cx = L.bodyX + L.bodyW / 2;
  L.cy = L.bodyY + L.bodyH / 2;
  return L;
}
```

Build the top plate from a rounded, stepped path; draw four recessed screw holes at `(40, 34)`, `(620, 34)`, `(40, 294)`, and `(620, 294)` in the 660×328 cover coordinate system; retain a dark square screen well; and add `.ssd-jikkey-mark` as a small blue pixel motif on the available face area.

- [ ] **Step 4: Render five front and three side controls with the existing channels**

Use one ordered control specification so DOM order and channel order remain explicit:

```javascript
var controls = [
  {name:"up", channel:CHANNEL.up, label:"Up", surface:"front", x:104, y:74},
  {name:"down", channel:CHANNEL.down, label:"Down", surface:"front", x:104, y:254},
  {name:"left", channel:CHANNEL.left, label:"Left", surface:"front", x:76, y:164},
  {name:"right", channel:CHANNEL.right, label:"Right", surface:"front", x:132, y:164},
  {name:"select", channel:CHANNEL.select, label:"Select", surface:"front", x:560, y:164},
  {name:"key1", channel:CHANNEL.key1, label:"Key 1", surface:"side", x:656, y:92},
  {name:"key2", channel:CHANNEL.key2, label:"Key 2", surface:"side", x:656, y:164},
  {name:"key3", channel:CHANNEL.key3, label:"Key 3", surface:"side", x:656, y:236}
];
```

Scale each coordinate by `L.u`, use narrow rounded rectangles for the four directions and the three side keys, and a circle for select. Emit control groups with:

```javascript
'<g class="ssd-ctl ssd-control--' + spec.surface + '"' +
' data-ssd-channel="' + spec.channel + '"' +
' data-ssd-control="' + spec.name + '" role="button" tabindex="0"' +
' aria-label="' + spec.label + '">'
```

Use `#0076ff` for hover/focus illumination and preserve a physical sink/translation on press.

- [ ] **Step 5: Add keyboard activation without double-sending**

Inside `bindControls`, add a `keydown` listener on the SVG. Enter and Space activate the focused control, prevent default, and stop propagation so `wallet.html` does not also send its global Enter/Space mapping:

```javascript
svgEl.addEventListener("keydown", function (event) {
  if (event.key !== "Enter" && event.key !== " ") return;
  var hit = event.target.closest && event.target.closest("[data-ssd-channel]");
  if (!hit) return;
  event.preventDefault();
  event.stopPropagation();
  hit.classList.add("ssd-down");
  onKey(parseInt(hit.getAttribute("data-ssd-channel"), 10));
  setTimeout(function () { hit.classList.remove("ssd-down"); }, PRESSED_MS);
});
```

Add a visible focus treatment using the existing group geometry and disable nonessential transitions under `prefers-reduced-motion`.

- [ ] **Step 6: Run interaction and geometry tests**

```bash
bash build/update-checksums.sh
python test/run.py device doom_layout
bash build/update-checksums.sh --check
```

Expected: all device pointer, touch, keyboard, square, fullscreen, and DOOM unlock checks PASS.

- [ ] **Step 7: Commit the shell slice**

```bash
git add src/web/seedsigner-device.js test/test_device.py build/checksums.txt
git commit -m "feat: render the JikKey cover and controls"
```

---

### Task 4: Apply the JikKey palette to all browser-owned UI

**Files:**
- Modify: `src/web/wallet.html:19-430`
- Modify: `src/web/wallet-cards.js:83-141`
- Modify: `src/web/wallet-coordinator.js:80-210`
- Modify: `src/web/wallet-tutorial.js:80-165, 447`
- Modify: `test/test_brand.py`
- Modify: `test/test_tray_layout.py:16-76`
- Modify: `build/checksums.txt`

**Interfaces:**
- Consumes: root `--accent: #0076ff` from Task 1.
- Produces: browser-owned active, hover, focus, progress, and success styling using JikKey Blue while red warnings remain red.

- [ ] **Step 1: Change tests to require the JikKey accent**

In `test/test_tray_layout.py`, set:

```python
ACCENT = "rgb(0, 118, 255)"
```

Rename the assertion to `"inserting accents the card in JikKey Blue"`.

Extend `test_brand.py` after loading `wallet.html`:

```python
page.locator("#firmware-switch button[data-choice=stock]").evaluate(
    "button => button.setAttribute('aria-pressed', 'true')")
check("firmware active state uses JikKey Blue",
      page.locator("#firmware-switch button[data-choice=stock]").evaluate(
          "node => getComputedStyle(node).borderTopColor") == "rgb(0, 118, 255)")
check("security warning remains red",
      page.locator("#warning").evaluate(
          "node => getComputedStyle(node).borderTopColor") != "rgb(0, 118, 255)")
```

- [ ] **Step 2: Run palette tests and verify they fail**

Run: `python test/run.py brand tray_layout`

Expected: FAIL because the active firmware and inserted card still use Bitcoin orange.

- [ ] **Step 3: Replace browser chrome accents**

In `wallet.html`, replace outer-UI `#f7931a` literals with `var(--accent)`. Do not change `.warn`, `#camera-hint`, `#status.err`, mainnet warning colors, or any pixels inside `#screen`.

In injected CSS strings in `wallet-cards.js`, `wallet-coordinator.js`, and `wallet-tutorial.js`, use `var(--accent,#0076ff)` so the components retain a safe local fallback. Replace the orange tray glow `rgba(247,147,26,.35)` with `rgba(0,118,255,.35)`. Change the tutorial canvas arrow stroke from `#f7931a` to `#0076ff` because Canvas cannot resolve a CSS variable.

Keep gold smartcard-chip metal colors unchanged; those describe the chip, not the page accent.

- [ ] **Step 4: Run focused palette and component tests**

```bash
bash build/update-checksums.sh
python test/run.py brand tray_layout firmware tutorial
bash build/update-checksums.sh --check
```

Expected: tests PASS; warning color assertions remain non-blue.

- [ ] **Step 5: Commit the palette slice**

```bash
git add src/web/wallet.html src/web/wallet-cards.js src/web/wallet-coordinator.js \
  src/web/wallet-tutorial.js test/test_brand.py test/test_tray_layout.py build/checksums.txt
git commit -m "feat: apply the JikKey interface palette"
```

---

### Task 5: Update square-screen baselines and documentation

**Files:**
- Modify: `test/harness.py:121-136`
- Modify: `test/run.py:140-204`
- Modify: `test/README.md`
- Modify: `README.md`
- Modify: `docs/ARCHITECTURE.md:109-118, 175-193`
- Modify: `docs/img/device.png`
- Modify: `test/baseline/screen-b2269592.png`
- Modify: `test/baseline/stock-screen-b2269592.png`
- Modify: `build/checksums.txt`

**Interfaces:**
- Consumes: 240×240 rendered firmware canvases and test artifacts from Tasks 2–4.
- Produces: auditable 240×240 known-good baselines and documentation that no longer claims a 320×240 SeedSigner Plus shell.

- [ ] **Step 1: Update geometry language before regenerating evidence**

Change `test/harness.py` `save_screen()` documentation to say it writes the native 240×240 firmware canvas. Change the `test/run.py` baseline explanation from 320×240 to 240×240 without weakening the statement that one changed pixel fails. Update `test/README.md` descriptions of device geometry and captured screens.

In `README.md` and `docs/ARCHITECTURE.md`, replace the emulated panel description with `st7789_240x240`, explain that the JikKey cover SVG is browser-owned UI around unmodified firmware, and retain the shared-memory and shim architecture explanations.

- [ ] **Step 2: Generate candidate square baselines**

Run the six scan captures:

```bash
python test/run.py scan_seedqr scan_compact scan_native \
  stock_scan_seedqr stock_scan_compact stock_scan_native
```

Expected at this point: individual scans reach `SeedFinalizeScreen`; the same-seed comparison may fail only because committed baselines are still 320×240.

- [ ] **Step 3: Verify candidate baseline semantics before copying**

Open `test/artifacts/scan-screen-qr.png` and `test/artifacts/stock-scan-screen-qr.png`. Confirm both are exactly 240×240 and visibly show fingerprint `b2269592`. Confirm each firmware's three captures are byte-identical:

```powershell
Get-FileHash test\artifacts\scan-screen-qr.png,test\artifacts\scan-screen-qr-compact.png,test\artifacts\scan-screen-native-compact.png
Get-FileHash test\artifacts\stock-scan-screen-qr.png,test\artifacts\stock-scan-screen-qr-compact.png,test\artifacts\stock-scan-screen-native-compact.png
```

Expected: one hash shared by the three smartcard files and one hash shared by the three stock files.

- [ ] **Step 4: Replace only the verified baselines and rerun comparisons**

Copy the verified files:

```powershell
Copy-Item test\artifacts\scan-screen-qr.png test\baseline\screen-b2269592.png
Copy-Item test\artifacts\stock-scan-screen-qr.png test\baseline\stock-screen-b2269592.png
```

Run: `python test/run.py scan`

Expected: all six scan tests and both same-seed baseline comparisons PASS.

- [ ] **Step 5: Capture the new documented device image**

Run `python test/run.py device`, then capture `#device` on a booted smartcard home screen with a Playwright viewport of 1200×900 and overwrite `docs/img/device.png`. The clip must contain the full JikKey shell, all eight controls, and the live 240×240 home screen without page header or footer.

- [ ] **Step 6: Refresh checksums and commit documentation evidence**

```bash
bash build/update-checksums.sh
bash build/update-checksums.sh --check
git add README.md docs/ARCHITECTURE.md docs/img/device.png test/README.md \
  test/harness.py test/run.py test/baseline/screen-b2269592.png \
  test/baseline/stock-screen-b2269592.png build/checksums.txt
git commit -m "docs: describe and verify the square JikKey device"
```

---

### Task 6: Run full verification and open the simulator

**Files:**
- Verify: all modified files
- Verify: `build/checksums.txt`

**Interfaces:**
- Consumes: complete JikKey simulator implementation.
- Produces: passing focused/full test evidence and a running local simulator opened for user inspection.

- [ ] **Step 1: Run fast structural checks**

```bash
python test/run.py leak_scan cards brand tray_layout device doom_layout firmware build_info
bash build/update-checksums.sh --check
```

Expected: every named check PASS and checksum manifest PASS.

- [ ] **Step 2: Run the complete offline browser suite**

Run: `python test/run.py`

Expected: all suite entries PASS for the firmware variants configured by `test/run.py`. If required build outputs are absent, allow the existing pinned build scripts to fetch/rebuild them, then rerun the same command.

- [ ] **Step 3: Inspect final browser states**

Serve the overlay with the existing isolated server:

```powershell
python test\serve.py --port 8770 src\web src\shims build\out
```

Inspect at desktop 1440×980 and mobile 390×844:

- JikKey logo loads with no white square.
- The screen is square and shows the live firmware without clipping.
- STEP-derived outline, four screws, five front controls, and three side controls are visible.
- Every control has hover/pressed/focus feedback and the screen remains inert.
- Firmware switch, card tray, tutorial, coordinator, and fullscreen use JikKey Blue.
- Warnings remain red and legible.
- No horizontal scrollbar or browser console errors appear.

- [ ] **Step 4: Open the final local simulator for the user**

Open `http://127.0.0.1:8770/wallet.html?wallet=1&firmware=smartcard` in the in-app browser, leaving the isolated server running for inspection.

- [ ] **Step 5: Record final repository state**

```bash
git status --short
git log --oneline -6
```

Expected: clean working tree and the focused implementation commits above.
