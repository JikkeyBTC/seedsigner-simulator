# JikKey Korean UI and sharp display implementation plan

**Goal:** Apply the supplied logo, orange suede page, Korean-first bilingual UI, then improve display rendering without moving the device's icons or changing wallet data.

**Architecture:** Web copy lives in a reversible Korean/English catalog. The website's language preference never reaches the firmware: its own settings control its screen language. Firmware calculations stay at 240×240; a display-only adapter renders text/vector operations at a higher output resolution using the native glyph bounds.

**Stack:** Existing vanilla JavaScript/SVG, Python/Pillow inside the existing Pyodide worker, Playwright tests.

**Specification:** The user's five requirements in this task, with the accepted STEP cover from the preceding turn as the geometry baseline.

## Constraints

- Preserve the STEP cover, button channel mappings, logical 240×240 coordinates, seed/card data, and protocol payloads.
- Implement theme, supplied logo and language switching before enabling HD output.
- Korean is the website default; an explicit `lang=en` or saved preference selects English. Firmware language remains entirely under device settings.
- Use concise Korean, 해요체 for explanations and concrete action labels. Do not translate seed words, addresses, keys, descriptors or passwords.
- A language switch must not reload the page or restart the worker.
- Keep changes in the existing `sandbox/0906_work` worktree. Preserve earlier uncommitted cover changes.

## 1. Web presentation and language switch

- [x] Add `src/web/jikkey-i18n.js`, stylesheet and original PNG logo.
- [x] Expose `JikKeyI18n.language`, `t(source, params)`, `setLanguage(language)` and the `jikkey-language-change` event.
- [x] Translate static and dynamic UI while preserving DOM/state and source text for switching back.
- [x] Test Korean defaults, persisted English, live switching and responsive header/device layout.

## 2. Firmware language isolation

- [x] Preserve the original firmware locale loading and device settings.
- [x] Keep website preferences out of worker init, input channels and firmware messages.
- [x] Remove the superseded browser firmware-translation adapter and catalog.
- [x] Test both firmware variants: web language switches leave canvas bytes, active menu, worker and key input unchanged.

## 3. High-resolution output

- [x] Keep native images and font metrics unchanged. Record drawing/compositing metadata only for presentation.
- [x] Render high-resolution glyph masks inside their original native ink bounds; preserve inclusive shape bounds and rounded crop offsets.
- [x] Send frame pixel dimensions separately from logical display dimensions. Resize canvas backing storage only, never the cover or firmware layout.
- [x] Keep camera/entropy and QR source data native; nearest-scale exact QR bitmaps. Bound intermediate allocations and fall back to a complete native frame on presentation failure.
- [x] Compare native frame bytes and icon bounds with high-resolution output enabled/disabled, then verify actual browser screenshots.

## 4. Verification

- [x] Run focused language and rendering tests, device/fullscreen tests, both firmware boots, card and QR/seed regressions appropriate to the modified paths.
- [x] Check Korean/English desktop and mobile screenshots against the accepted cover.
- [x] Review the final diff, check JavaScript/Python syntax and whitespace, and present the running local simulator.

## Verification evidence

- 15 HD tests passed with local Pillow and bundled Pyodide/Pillow 10.2.0. Original native image bytes, metrics and component geometry also matched for Icon, Button, TextArea and BtcAmount from both firmware ZIPs.
- Both firmware variants boot with 240×240 logical dimensions and 1920×1920 output. Web language round trips preserve exact canvas bytes, the selected menu and the existing worker.
- Eight web i18n tests pass, including state retention, exact device-menu names in instructions and Escape dismissal from language controls.
- Native and HD QR readers and tutorial mirrors decode the same payload. Camera tests decoded both SeedQR and CompactSeedQR; stock camera preview/capture and smartcard PIN/empty-card flows passed.
- Device registration at 320, 375, 768 and 1440px, portrait/landscape fullscreen, all eight input channels, card tray, DOOM handoff and device setting changes passed.
- The supplied logo and installed PNG have identical SHA-256 hashes. Final desktop/phone/fullscreen captures are in the task workspace's `output` folder.
