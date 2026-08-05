# JikKey simulator redesign

Date: 2026-08-05
Status: Approved

## Goal

Rebrand the existing MIT-licensed SeedSigner and ShieldSigner simulator as JikKey while preserving its existing simulator behavior. Replace the current SeedSigner Plus-style shell with a responsive vector shell derived from the supplied JikKey cover STEP model, and boot both firmware variants with their native 240×240 display configuration.

## Source references

- Simulator repository: `C:/Users/Admin/GIT/seedsigner-simulator`
- Product cover: `D:/스마트스토어/Seedsigner_HAT/양산/final/cover.step`
- JikKey vector logo: `D:/스마트스토어/seedsigner/상표관련/로고/직키로고/svg/svg_output/logo_7.svg`
- JikKey raster logo reference: `D:/스마트스토어/seedsigner/상표관련/로고/직키로고/직키로고-01.png`

The STEP model contains a single physical cover body approximately 66.0 × 32.8 × 6.72 mm. Its visible front features are four corner screw holes, a central display opening, four directional button openings on the left, and a circular select button opening on the right.

The logo establishes JikKey Blue `#0076FF` with black and white as the supporting palette.

## Selected approach

Implement a CAD-derived SVG shell in the existing vanilla HTML, CSS, and JavaScript stack. Do not use a raster render as the interactive surface and do not add a framework or UI dependency.

This approach preserves precise hit targets and responsive scaling while expressing the supplied product geometry. A raster or 3D-rendered shell would make pointer alignment and mobile scaling less reliable. A minimal flat shell would not carry enough of the product identity.

## Visual design

### Page chrome

- Rename the page-facing product to **JikKey Simulator**.
- Use a cleaned, transparent version of the supplied SVG logo. Retain the original logo geometry and `#0076FF` color.
- Replace outer simulator orange accents with JikKey Blue, including focus rings, pressed states, firmware controls, fullscreen controls, links, and the smartcard tray.
- Keep warning red for security-critical messages and preserve readable neutral grays for secondary information.
- Keep the existing page information hierarchy and safety warning before the device.
- Keep SeedSigner and ShieldSigner firmware names wherever they identify the actual upstream firmware.

### Device shell

- Rebuild the shell in `seedsigner-device.js` as a responsive SVG derived from the STEP model's front view and proportions.
- Preserve the STEP model's stepped perimeter, rounded corners, four screw holes, central screen opening, four left directional controls, and circular right select control.
- Use a matte graphite body, dark neutral controls, restrained edge highlights, and a JikKey Blue active state.
- Place a compact JikKey mark on the shell without obscuring the screen or controls; show the full supplied logo in the page header where its proportions remain legible.
- Add three slim buttons to the right side edge for `key1`, `key2`, and `key3`. They must appear as part of the case, remain individually clickable and touchable, and expose accessible labels.
- Preserve the rule that the display itself is not a pointer or touch control.
- Maintain the existing responsive device scaling and mobile fullscreen behavior.

### Interaction states

- Pointer hover may lift or brighten a button slightly.
- Pointer, touch, and keyboard press states use translation or scale with a 200–250 ms transition.
- Keyboard focus uses a visible JikKey Blue ring.
- Pressed states must not depend on color alone; use position, highlight, or border changes as a second cue.
- Respect `prefers-reduced-motion` by removing nonessential transitions.

## Firmware display configuration

- Change the simulator-created firmware settings from `st7789_320x240` to `st7789_240x240` for both stock SeedSigner and ShieldSigner.
- Start the page canvas at 240×240 so the shell does not jump while the worker boots.
- Continue treating the worker's reported renderer dimensions as the source of truth. If a firmware reports another size, resize the canvas and shell safely rather than refusing to run.
- Preserve Testnet as the initial network and leave every firmware setting reachable through the existing menus.
- Do not modify upstream firmware source files inside the wallet archive.

## Input and data flow

The redesign must not change the existing key channels or transport:

| Visible control | Existing channel |
| --- | --- |
| Direction up | `up` |
| Direction down | `down` |
| Direction left | `left` |
| Direction right | `right` |
| Circular select | `select` |
| Side button 1 | `key1` |
| Side button 2 | `key2` |
| Side button 3 | `key3` |

Pointer and touch input continue through the device component's `onKey` callback. Keyboard events continue through the current page key map and shared key buffer. The worker continues to paint raw firmware frames into the single canvas. Camera, QR, card, tutorial, coordinator, firmware switching, and wallet panels retain their current interfaces.

## DOOM compatibility

- Keep DOOM available and keep the `key1 → key2 → key3` unlock sequence.
- Align the browser boot-game panel constants and frame buffer with the 240×240 device.
- Do not stretch or crop DOOM frames. Use the native square output expected by the original SeedSigner boot-game port.
- Preserve the existing fallback that gives control to the wallet if DOOM assets are absent or fail to load.

## Assets and security

- Copy a sanitized JikKey logo into the web assets and remove the opaque white background path from the web version.
- Serve all branding assets locally so the current content security policy requires no new origin.
- If the logo fails to load, the page title remains readable as text.
- Preserve the existing COOP, COEP, and CSP behavior.
- Preserve `LICENSE`, `THIRD-PARTY.md`, upstream credits, and the statement that the project is independent and not endorsed by upstream SeedSigner projects.

## Error handling

- A non-240 renderer size triggers the existing dynamic shell rebuild and a diagnostic message in debug mode; it does not block the wallet.
- Missing DOOM assets fall back to the wallet through the existing `onUnavailable` path.
- Missing logo assets do not block controls or firmware loading.
- Existing camera, worker, card, and network errors retain their current behavior and messages except for visual restyling required by the new palette.

## Testing

### Focused browser tests

- Assert that the initial and booted firmware canvas is 240×240 for SeedSigner and ShieldSigner.
- Assert a square screen slot at desktop and mobile sizes, including fullscreen mode.
- Assert the presence of the JikKey logo, CAD-derived shell markers, five front controls, and three side controls.
- Assert that every visible control maps to its existing channel.
- Assert that clicking or tapping the screen sends no key.
- Assert one pointer or touch press produces exactly one key event and holding a touch does not repeat.
- Assert keyboard focus, `aria-label`, and pressed-state behavior for all controls.
- Assert the page has no horizontal overflow at narrow widths.
- Assert outer UI accents resolve to `#0076FF` while security warnings retain their warning color.

### Existing functional coverage

- Run the existing device, settings, firmware, scan, QR, password, image-entropy, mainnet, smartcard, tutorial, and wallet tests for both firmware variants where the repository's test runner supports them.
- Update assertions and documentation that encode the old 320×240 or 4:3 geometry.
- Regenerate only visual baselines whose pixels legitimately change because the firmware now renders its 240×240 layout. Do not weaken semantic assertions.
- Exercise DOOM startup and its side-button unlock before claiming full behavior preservation.

## Documentation updates

Update page copy, README, architecture documentation, and test documentation where they claim a 320×240 SeedSigner Plus panel or show the old shell. Keep the technical explanation of the real upstream firmware, browser shims, reproducible builds, and security limitations intact.

## Non-goals

- No firmware feature additions or menu changes.
- No network, wallet, seed, signing, or smartcard logic changes.
- No framework migration.
- No remote font, icon, analytics, or branding dependency.
- No removal of upstream names, license notices, or security warnings.

## Acceptance criteria

The work is complete when both firmware variants boot with `st7789_240x240`, the canvas and device screen are square, the shell visually follows the supplied STEP cover and JikKey identity, all eight inputs remain usable by pointer/touch/keyboard, and the relevant existing functional tests pass without reducing their coverage.
