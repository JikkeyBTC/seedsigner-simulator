/*
 * JikKey cover, measured from the supplied [0901]cover.step front face.
 * The 69.8 x 32.7 mm cover has R5 corners, a 1 mm chamfer, four countersunk
 * fasteners, a joystick opening and three integral button tabs. Its 25 mm
 * square display opening is fixed physical geometry, independent of firmware
 * resolution. All dimensions below share the same SVG coordinate system.
 *
 * Standalone on purpose: nothing here touches SharedArrayBuffer, a worker or a
 * camera, so the same file can dress the live simulator and a marketing page
 * that has none of that. The only way out is the onKey callback.
 *
 * Everything is drawn rather than loaded because the pages using this send a CSP
 * with no external image, font or script origins.
 *
 * Lighting is one key from the upper left plus a soft fill. Anything shaded by a
 * gradient of its own would light itself in isolation and break that, so the
 * scene-wide paints below are userSpaceOnUse: a key near the bottom right is
 * darker than the same key near the top left because it samples a different
 * part of the same light.
 *
 * The screen cutout is published as a percentage of the viewBox, never as pixels,
 * so the live canvas keeps registration with the art at any rendered width.
 */
(function (global) {
  "use strict";

  var doc = global.document;
  if (!doc) return;

  var STYLE_ID = "ssd-style";
  var instances = 0;

  // Index into the wallet's BUTTON_NAMES. Mirrored rather than imported so this
  // file keeps no wallet dependency.
  var CHANNEL = {
    up: 1, down: 2, left: 3, right: 4, select: 5, key1: 6, key2: 7, key3: 8,
  };

  var CSS = [
    // No tap highlight and no selection: a thumb on a key must not paint a blue
    // box over it or start selecting the shell.
    ".ssd-root{position:relative;display:inline-block;line-height:0;max-width:100%;",
    "touch-action:manipulation;-webkit-tap-highlight-color:transparent;",
    "-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}",
    ".ssd-svg{display:block;width:100%;height:auto}",
    // Percentage geometry, so the cutout tracks the art through any resize.
    ".ssd-screen-slot{position:absolute;z-index:2;overflow:hidden;background:#000}",
    ".ssd-screen-slot>canvas{display:block;width:100%;height:100%;object-fit:contain}",
    ".ssd-glass{position:absolute;z-index:3;pointer-events:none}",
    ".ssd-ctl{pointer-events:none}",
    ".ssd-ctl .ssd-hover,.ssd-ctl .ssd-press{opacity:0}",
    // Only a live device reacts; the decorative build stays inert illustration.
    ".ssd-live .ssd-ctl{pointer-events:auto;cursor:pointer}",
    ".ssd-live .ssd-cap{transition:transform .07s ease-out}",
    ".ssd-live .ssd-ctl .ssd-hover{transition:opacity .13s ease}",
    // Hover only where there is a pointer that can hover. A touch that lands on
    // a key would otherwise leave it lit until something else was touched.
    "@media (hover:hover){.ssd-live .ssd-ctl:hover .ssd-hover{opacity:.2}}",
    // Pressed is a class rather than :active, because :active under touch is
    // whatever the browser feels like: Safari does not apply it at all without a
    // touch handler, and every engine drops it the moment a finger drifts. The
    // class goes on when the key is pressed and stays long enough to be seen.
    // The cap sinks, not the whole key: it goes down into its own side wall, so
    // the wall shortens under a press the way a real one does.
    ".ssd-live .ssd-ctl.ssd-down .ssd-cap{transform:translateY(var(--ssd-sink,2px))}",
    ".ssd-live .ssd-ctl.ssd-down .ssd-press{opacity:.42}",
    ".ssd-live .ssd-ctl.ssd-down .ssd-hover{opacity:.1}",
    "@media (prefers-reduced-motion:reduce){.ssd-live .ssd-ctl,",
    ".ssd-live .ssd-ctl .ssd-hover{transition:none}}",
  ].join("\n");

  // How long a key stays visibly down. A tap can be over in 40 milliseconds,
  // which is not long enough to see, so the state is held to this floor.
  var PRESSED_MS = 130;

  /**
   * One press per finger, from a drawn key and nowhere else.
   *
   * pointerdown rather than click: a key has to answer where a thumb lands,
   * and click arrives up to 300ms later on a phone. Nothing listens for mouse
   * events alongside it either, because a touch synthesises a mousedown of its
   * own afterwards and a device that answered both would send every key twice;
   * preventDefault here stops that synthesis, and with it the long-press menu
   * and the text selection, none of which a hardware button has.
   *
   * The pointer is remembered until it lifts, so a finger held on a key is one
   * press and no repeat -- the real device does not auto-repeat either -- and a
   * second finger arriving while the first is down is not a second press.
   */
  function bindControls(svgEl, onKey) {
    var pointer = null;    // the pointer holding a key down, if any
    var key = null;        // and the key it is holding
    var since = 0;

    function release() {
      if (!key) return;
      var released = key, waited = Date.now() - since;
      key = null;
      pointer = null;
      if (waited >= PRESSED_MS) released.classList.remove("ssd-down");
      else setTimeout(function () { released.classList.remove("ssd-down"); },
                      PRESSED_MS - waited);
    }

    function begin(event) {
      if (event.isPrimary === false) return;
      var hit = event.target.closest && event.target.closest("[data-ssd-channel]");
      if (!hit) return;
      event.preventDefault();
      // Any press still open ends here rather than wedging the device shut if
      // its pointerup was never delivered.
      release();
      key = hit;
      pointer = event.pointerId;
      since = Date.now();
      hit.classList.add("ssd-down");
      onKey(parseInt(hit.getAttribute("data-ssd-channel"), 10));
    }

    if (global.PointerEvent) {
      svgEl.addEventListener("pointerdown", begin);
      // On the window: a finger that slides off the key before it lifts still
      // ends the press, and so does the browser taking the gesture away.
      var end = function (event) { if (pointer === event.pointerId) release(); };
      global.addEventListener("pointerup", end);
      global.addEventListener("pointercancel", end);
    } else {
      svgEl.addEventListener("mousedown", begin);
      global.addEventListener("mouseup", release);
    }
  }

  function injectStyle() {
    if (doc.getElementById(STYLE_ID)) return;
    var el = doc.createElement("style");
    el.id = STYLE_ID;
    el.textContent = CSS;
    (doc.head || doc.documentElement).appendChild(el);
  }

  function n(v) { return Math.round(v * 100) / 100; }
  function pct(a, b) { return (a / b * 100).toFixed(6) + "%"; }

  function roundRectPath(x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    return "M" + n(x + r) + " " + n(y) + "H" + n(x + w - r) +
      "a" + n(r) + " " + n(r) + " 0 0 1 " + n(r) + " " + n(r) +
      "V" + n(y + h - r) +
      "a" + n(r) + " " + n(r) + " 0 0 1 " + n(-r) + " " + n(r) +
      "H" + n(x + r) +
      "a" + n(r) + " " + n(r) + " 0 0 1 " + n(-r) + " " + n(-r) +
      "V" + n(y + r) +
      "a" + n(r) + " " + n(r) + " 0 0 1 " + n(r) + " " + n(-r) + "Z";
  }

  // STEP XY coordinates are translated to the cover's top-left corner, with
  // Y pointing down. The chamfer mouth is 26.54 mm; its clear opening is 25 mm.
  // Render resolution changes sampling, never these physical proportions.
  function layout(screenH, scale, withCard) {
    var sh = Math.round(screenH * scale);
    var mm = sh / 25;
    var u = sh / 480;
    var L = { u: u, mm: mm, sw: sh, sh: sh };
    L.edge = mm;
    L.bodyW = 69.8 * mm;
    L.bodyH = 32.7 * mm;
    L.radius = 5 * mm;
    L.withCard = withCard;
    L.cardW = 500 * u;
    L.cardH = 300 * u;
    L.cardBite = 44 * u;
    L.padX = 1.8 * mm;
    L.padT = 2 * mm;
    L.padB = withCard ? L.cardH - L.cardBite + 44 * u : 4.2 * mm;
    L.bodyX = L.padX;
    L.bodyY = L.padT;
    L.viewW = L.bodyW + L.padX * 2;
    L.viewH = L.bodyH + L.padT + L.padB;
    L.screenX = L.bodyX + 22.29528 * mm;
    L.screenY = L.bodyY + 3.94644 * mm;
    L.cx = L.bodyX + L.bodyW / 2;
    L.cy = L.bodyY + L.bodyH / 2;
    L.padCx = L.bodyX + 10.74528 * mm;
    L.padCy = L.bodyY + 16.78644 * mm;
    L.cardX = L.bodyX + L.bodyW * 0.53 - L.cardW / 2;
    L.cardY = L.bodyY + L.bodyH - L.cardBite;
    return L;
  }

  // The cover's projected polylines and Beziers use only coordinate pairs.
  function coverPath(path, L) {
    return path.replace(/(-?\d*\.?\d+)[ ,]+(-?\d*\.?\d+)/g, function (_, x, y) {
      return n(L.bodyX + Number(x) * L.mm) + "," + n(L.bodyY + Number(y) * L.mm);
    });
  }

  function defs(id, L) {
    var u = L.u;
    var space = 'gradientUnits="userSpaceOnUse"';
    var bodyBox = ' x1="' + n(L.bodyX) + '" y1="' + n(L.bodyY) + '" x2="' +
      n(L.bodyX + L.bodyW) + '" y2="' + n(L.bodyY + L.bodyH) + '"';
    return [
      "<defs>",
      '<radialGradient id="', id, '-stick" cx=".4" cy=".32" r=".7">',
      '<stop offset="0" stop-color="#34383b"/>',
      '<stop offset=".65" stop-color="#24272a"/>',
      '<stop offset=".88" stop-color="#16191c"/>',
      '<stop offset="1" stop-color="#3e4347"/></radialGradient>',
      // Shell top face: key light upper-left, falling away to the lower right.
      // Flatter than a glossy consumer shell: the real one is a matte grey.
      '<linearGradient id="', id, '-body" ', space, bodyBox, ">",
      '<stop offset="0" stop-color="#55585c"/>',
      '<stop offset=".40" stop-color="#45484c"/>',
      '<stop offset=".75" stop-color="#383b3f"/>',
      '<stop offset="1" stop-color="#2e3134"/>',
      "</linearGradient>",
      // A chamfer facet is lit by its own orientation, not by where it sits, so
      // the bevel is shaded per edge: these run across the whole ring and
      // brighten the up-facing and left-facing facets along their full length.
      '<linearGradient id="', id, '-chamV" x1="0" y1="0" x2="0" y2="1">',
      '<stop offset="0" stop-color="#ffffff" stop-opacity=".6"/>',
      '<stop offset="', n(L.edge / L.bodyH * 0.85), '" stop-color="#ffffff" stop-opacity=".46"/>',
      '<stop offset="', n(L.edge / L.bodyH * 2.2), '" stop-color="#ffffff" stop-opacity=".08"/>',
      '<stop offset=".12" stop-color="#ffffff" stop-opacity="0"/>',
      '<stop offset=".88" stop-color="#000000" stop-opacity="0"/>',
      '<stop offset="', n(1 - L.edge / L.bodyH * 1.1), '" stop-color="#000000" stop-opacity=".2"/>',
      '<stop offset="1" stop-color="#000000" stop-opacity=".46"/>',
      "</linearGradient>",
      '<linearGradient id="', id, '-chamH" x1="0" y1="0" x2="1" y2="0">',
      '<stop offset="0" stop-color="#ffffff" stop-opacity=".34"/>',
      '<stop offset="', n(L.edge / L.bodyW * 0.85), '" stop-color="#ffffff" stop-opacity=".26"/>',
      '<stop offset="', n(L.edge / L.bodyW * 2.2), '" stop-color="#ffffff" stop-opacity=".05"/>',
      '<stop offset=".12" stop-color="#ffffff" stop-opacity="0"/>',
      '<stop offset=".88" stop-color="#000000" stop-opacity="0"/>',
      '<stop offset="', n(1 - L.edge / L.bodyW * 1.1), '" stop-color="#000000" stop-opacity=".18"/>',
      '<stop offset="1" stop-color="#000000" stop-opacity=".4"/>',
      "</linearGradient>",
      '<linearGradient id="', id, '-chamD" x1="0" y1="0" x2="1" y2="1">',
      '<stop offset="0" stop-color="#ffffff" stop-opacity=".13"/>',
      '<stop offset=".32" stop-color="#ffffff" stop-opacity="0"/>',
      '<stop offset=".45" stop-color="#000000" stop-opacity="0"/>',
      '<stop offset="1" stop-color="#000000" stop-opacity=".13"/>',
      "</linearGradient>",
      // A broad soft source skimming the face, which is most of what separates a
      // photographed shell from a filled rectangle.
      '<linearGradient id="', id, '-sheen" ', space,
      ' x1="', n(L.bodyX), '" y1="', n(L.bodyY), '" x2="',
      n(L.bodyX + L.bodyW * 0.78), '" y2="', n(L.bodyY + L.bodyH), '">',
      '<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>',
      '<stop offset=".14" stop-color="#ffffff" stop-opacity=".045"/>',
      '<stop offset=".26" stop-color="#ffffff" stop-opacity=".012"/>',
      '<stop offset=".44" stop-color="#ffffff" stop-opacity="0"/>',
      "</linearGradient>",
      // Same facet inverted: a recess turns its lit wall towards the lower right.
      '<linearGradient id="', id, '-recess" x1="0" y1="0" x2="1" y2="1">',
      '<stop offset="0" stop-color="#0c0e11"/>',
      '<stop offset=".35" stop-color="#181b20"/>',
      '<stop offset=".72" stop-color="#3c424b"/>',
      '<stop offset="1" stop-color="#59606b"/>',
      "</linearGradient>",
      '<radialGradient id="', id, '-keylight" ', space,
      ' cx="', n(L.bodyX + L.bodyW * 0.2), '" cy="', n(L.bodyY + L.bodyH * 0.05),
      '" r="', n(L.bodyW * 0.95), '">',
      '<stop offset="0" stop-color="#ffffff" stop-opacity=".09"/>',
      '<stop offset=".55" stop-color="#ffffff" stop-opacity=".016"/>',
      '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>',
      "</radialGradient>",
      // The one light every raised part is graded against.
      '<linearGradient id="', id, '-scene" ', space, bodyBox, ">",
      '<stop offset="0" stop-color="#ffffff" stop-opacity=".07"/>',
      '<stop offset=".42" stop-color="#ffffff" stop-opacity="0"/>',
      '<stop offset=".52" stop-color="#000000" stop-opacity="0"/>',
      '<stop offset="1" stop-color="#000000" stop-opacity=".09"/>',
      "</linearGradient>",
      // The smartcard: dark matte PVC catching the same key light.
      '<linearGradient id="', id, '-card" ', space,
      ' x1="', n(L.cardX), '" y1="', n(L.cardY), '" x2="', n(L.cardX + L.cardW),
      '" y2="', n(L.cardY + L.cardH), '">',
      '<stop offset="0" stop-color="#2e3238"/>',
      '<stop offset=".45" stop-color="#1e2126"/>',
      '<stop offset="1" stop-color="#131518"/>',
      "</linearGradient>",
      // Two shadows: a tight contact patch, and a wide ambient one that lifts the
      // device off a page nearly as dark as the shadow itself.
      '<filter id="', id, '-drop" x="-40%" y="-40%" width="180%" height="200%">',
      '<feDropShadow dx="0" dy="', n(26 * u), '" stdDeviation="', n(32 * u),
      '" flood-color="#000000" flood-opacity=".55"/>',
      "</filter>",
      '<filter id="', id, '-contact" x="-40%" y="-200%" width="180%" height="500%">',
      '<feGaussianBlur stdDeviation="', n(9 * u), '"/>',
      "</filter>",
      // Matte plastic: without a little grain the gradients read as vector fills.
      '<filter id="', id, '-grain" x="0" y="0" width="100%" height="100%">',
      '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>',
      '<feColorMatrix type="saturate" values="0"/>',
      "</filter>",
      "</defs>",
    ].join("");
  }

  // Drawn before the shell so the front edge overlaps its top: the card is
  // inserted, not resting on top.
  function cardArt(id, L) {
    var u = L.u, out = [];
    var r = 10 * u;

    out.push('<ellipse cx="', n(L.cardX + L.cardW / 2), '" cy="', n(L.cardY + L.cardH),
      '" rx="', n(L.cardW * 0.46), '" ry="', n(9 * u),
      '" fill="#000000" opacity=".55" filter="url(#', id, '-contact)"/>');

    out.push('<rect x="', n(L.cardX), '" y="', n(L.cardY), '" width="', n(L.cardW),
      '" height="', n(L.cardH), '" rx="', n(r), '" fill="url(#', id, '-card)"/>');
    out.push('<rect x="', n(L.cardX), '" y="', n(L.cardY), '" width="', n(L.cardW),
      '" height="', n(L.cardH), '" rx="', n(r),
      '" fill="none" stroke="#000000" stroke-opacity=".5" stroke-width="', n(1.8 * u), '"/>');
    // Top-left lit lip, the only edge of the card facing the key light.
    out.push('<path d="M', n(L.cardX + r), ' ', n(L.cardY), 'H', n(L.cardX + L.cardW - r),
      'M', n(L.cardX), ' ', n(L.cardY + L.cardH - r), 'V', n(L.cardY + r),
      '" fill="none" stroke="#ffffff" stroke-opacity=".12" stroke-width="', n(1.6 * u), '"/>');
    return out.join("");
  }

  function bodyArt(id, L) {
    var u = L.u, x = L.bodyX, y = L.bodyY, w = L.bodyW, h = L.bodyH;
    var ix = x + L.edge, iy = y + L.edge;
    var iw = w - L.edge * 2, ih = h - L.edge * 2;
    var outer = roundRectPath(x, y, w, h, L.radius);
    var inner = roundRectPath(ix, iy, iw, ih, L.radius - L.edge);
    var band = ' d="' + outer + inner + '" fill-rule="evenodd"';
    var out = [];

    out.push('<ellipse cx="', n(x + w / 2), '" cy="', n(y + h + 5 * u),
      '" rx="', n(w * 0.44), '" ry="', n(11 * u),
      '" fill="#000000" opacity=".7" filter="url(#', id, '-contact)"/>');

    out.push('<path class="ssd-cover" d="', outer, '" fill="#23262b" filter="url(#', id, '-drop)"/>');
    out.push('<path', band, ' fill="#42464d"/>');
    out.push('<path', band, ' fill="url(#', id, '-chamV)"/>');
    out.push('<path', band, ' fill="url(#', id, '-chamH)"/>');
    out.push('<path', band, ' fill="url(#', id, '-chamD)"/>');
    out.push('<path d="', outer, '" fill="none" stroke="#d5d9dd" stroke-opacity=".14"',
      ' stroke-width="', n(1.2 * u), '"/>');

    out.push('<clipPath id="', id, '-face"><path d="', inner, '"/></clipPath>');
    out.push('<path d="', inner, '" fill="url(#', id, '-body)"/>');
    out.push('<path d="', inner, '" fill="url(#', id, '-keylight)"/>');
    out.push('<path d="', inner, '" fill="url(#', id, '-sheen)"/>');
    out.push('<g clip-path="url(#', id, '-face)"><rect x="', n(ix), '" y="', n(iy),
      '" width="', n(iw), '" height="', n(ih), '" filter="url(#', id,
      '-grain)" opacity=".055" style="mix-blend-mode:overlay"/></g>');
    return out.join("");
  }

  function screenArt(id, L) {
    var x = L.screenX, y = L.screenY, s = L.sw, bevel = 0.77 * L.mm;
    return [
      '<rect x="', n(x - bevel), '" y="', n(y - bevel), '" width="',
      n(s + bevel * 2), '" height="', n(s + bevel * 2),
      '" fill="url(#', id, '-recess)"/>',
      '<path d="M', n(x - bevel), ' ', n(y - bevel), 'L', n(x), ' ', n(y),
      'H', n(x + s), 'L', n(x + s + bevel), ' ', n(y - bevel),
      'Z" fill="#101316" opacity=".6"/>',
      // This rect is the actual clear opening; the HTML canvas uses exactly
      // these coordinates, rather than the wider mouth of the chamfer.
      '<rect class="ssd-screen-window" x="', n(x), '" y="', n(y),
      '" width="', n(s), '" height="', n(s), '" fill="#050607"/>',
    ].join("");
  }

  function screwArt(id, L) {
    var mm = L.mm, out = [];
    [[7.29973, 4.85], [65.29973, 4.85],
     [7.29973, 27.85], [65.29973, 27.85]].forEach(function (position) {
      var x = L.bodyX + position[0] * mm, y = L.bodyY + position[1] * mm;
      out.push('<g class="ssd-fastener">',
        '<circle cx="', n(x), '" cy="', n(y), '" r="', n(2.6 * mm),
        '" fill="url(#', id, '-recess)" stroke="#a1a8ae" stroke-opacity=".22"',
        ' stroke-width="', n(0.06 * mm), '"/>',
        '<circle cx="', n(x), '" cy="', n(y), '" r="', n(1.34 * mm),
        '" fill="#111417"/>',
        '<circle cx="', n(x), '" cy="', n(y), '" r="', n(1.12 * mm),
        '" fill="#383e43" stroke="#697178" stroke-width="', n(0.07 * mm), '"/>',
        '<path d="M', n(x - 0.55 * mm), ' ', n(y), 'h', n(1.1 * mm),
        'M', n(x), ' ', n(y - 0.55 * mm), 'v', n(1.1 * mm),
        '" stroke="#101315" stroke-width="', n(0.24 * mm),
        '" stroke-linecap="round"/></g>');
    });
    return out.join("");
  }

  function coverControl(name, label, L, content, live) {
    return '<g class="ssd-ctl" data-ssd-control="' + name +
      '" data-ssd-channel="' + CHANNEL[name] + '" role="button" aria-label="' + label +
      '" style="--ssd-sink:' + n(0.12 * L.mm) + 'px">' +
      (live ? '<title>' + label + '</title>' : '') + content + '</g>';
  }

  function padArt(id, L, live) {
    var mm = L.mm, cx = L.padCx, cy = L.padCy;
    var out = [
      '<circle cx="', n(cx), '" cy="', n(cy), '" r="', n(6.15 * mm),
      '" fill="#171b1e" stroke="#111416" stroke-width="', n(0.16 * mm), '"/>',
      '<circle cx="', n(cx), '" cy="', n(cy), '" r="', n(5.75 * mm),
      '" fill="none" stroke="#5c646b" stroke-opacity=".38" stroke-width="', n(0.08 * mm), '"/>',
    ];
    // Four tilt targets around one joystick, plus its centre press. The same
    // eight channels still reach the existing wallet and boot-game handlers.
    var outer = 6.8 * mm, inner = 3.25 * mm;
    var a = outer / Math.sqrt(2), b = inner / Math.sqrt(2);
    var sector = 'M' + n(cx - a) + ' ' + n(cy - a) + 'A' + n(outer) + ' ' +
      n(outer) + ' 0 0 1 ' + n(cx + a) + ' ' + n(cy - a) +
      'L' + n(cx + b) + ' ' + n(cy - b) + 'A' + n(inner) + ' ' + n(inner) +
      ' 0 0 0 ' + n(cx - b) + ' ' + n(cy - b) + 'Z';
    [["up", "Up", 0], ["right", "Right", 90],
     ["down", "Down", 180], ["left", "Left", 270]].forEach(function (key) {
      var content = [
        '<g transform="rotate(', key[2], ' ', n(cx), ' ', n(cy), ')">',
        '<path d="', sector, '" fill="transparent"/>',
        '<path class="ssd-hover" d="', sector, '" fill="#9ea7ad"/>',
        '<path class="ssd-press" d="', sector, '" fill="#080b0e"/>',
        '<g class="ssd-cap"><path d="M', n(cx - 0.55 * mm), ' ', n(cy - 4.6 * mm),
        'L', n(cx), ' ', n(cy - 5.2 * mm), 'L', n(cx + 0.55 * mm), ' ', n(cy - 4.6 * mm),
        '" fill="none" stroke="#969ea4" stroke-opacity=".7" stroke-width="', n(0.14 * mm),
        '" stroke-linecap="round" stroke-linejoin="round"/></g></g>',
      ].join("");
      out.push(coverControl(key[0], key[1], L, content, live));
    });
    out.push(coverControl("select", "Select", L, [
      '<circle cx="', n(cx), '" cy="', n(cy + 0.08 * mm), '" r="', n(3.18 * mm),
      '" fill="#0b0e10"/>',
      '<g class="ssd-cap">',
      '<circle cx="', n(cx), '" cy="', n(cy), '" r="', n(3.05 * mm),
      '" fill="url(#', id, '-stick)" stroke="#596168" stroke-opacity=".6"',
      ' stroke-width="', n(0.08 * mm), '"/>',
      '<circle cx="', n(cx), '" cy="', n(cy), '" r="', n(2.65 * mm),
      '" fill="none" stroke="#0d1013" stroke-opacity=".65" stroke-width="', n(0.07 * mm), '"/>',
      '<circle class="ssd-hover" cx="', n(cx), '" cy="', n(cy),
      '" r="', n(3.05 * mm), '" fill="#919ba3"/>',
      '<circle class="ssd-press" cx="', n(cx), '" cy="', n(cy),
      '" r="', n(3.05 * mm), '" fill="#000"/>',
      '</g>',
    ].join(""), live));
    return out.join("");
  }

  function keysArt(id, L, live) {
    // Front-face cut line from the STEP, sampled at 0.03 mm deflection. The
    // three tabs stay attached along their left edge, as on the supplied cover.
    var gap = coverPath(
      'M60.439,4.946L65.17,9.678L65.287,9.961L65.287,22.882L65.17,23.165' +
      'L60.389,27.946L53.295,27.946L53.295,25.146L59.291,25.146L59.602,25.138' +
      'L59.913,25.114L61.058,24.884L62.188,24.426L62.54,24.196L62.873,23.919' +
      'L63.524,23.15L64.054,22.161L64.146,21.843L64.162,21.509L64.029,21.092' +
      'L63.767,20.835L63.421,20.746L53.295,20.746L53.295,18.646L63.599,18.646' +
      'L63.599,14.246L53.295,14.246L53.295,12.146L63.421,12.146L63.672,12.101' +
      'L63.886,11.969L64.073,11.719L64.163,11.376L64.149,11.063L64.054,10.732' +
      'L63.524,9.742L62.873,8.974L62.561,8.712L62.188,8.466L61.058,8.009' +
      'L59.913,7.779L59.602,7.754L59.291,7.746L53.295,7.746L53.295,4.946Z', L);
    var out = ['<path d="', gap, '" fill="url(#', id, '-recess)"',
      ' stroke="#15191d" stroke-opacity=".6" stroke-width="', n(0.06 * L.mm), '"/>'];
    var tabs = [
      'M53.295,7.746L59.291,7.746C61.9,7.746 63.4,9.15 64.054,10.732' +
        'C64.38,11.45 64.01,12.146 63.421,12.146L53.295,12.146Z',
      'M53.295,14.246L63.599,14.246L63.599,18.646L53.295,18.646Z',
      'M53.295,20.746L63.421,20.746C64.01,20.746 64.38,21.44 64.054,22.161' +
        'C63.4,23.75 61.9,25.146 59.291,25.146L53.295,25.146Z',
    ];
    tabs.forEach(function (tab, index) {
      var path = coverPath(tab, L);
      out.push(coverControl('key' + (index + 1), 'Key ' + (index + 1), L, [
        '<g class="ssd-cap">',
        '<path d="', path, '" fill="url(#', id, '-body)"/>',
        '<path d="', path, '" fill="url(#', id, '-scene)"/>',
        '<path class="ssd-hover" d="', path, '" fill="#b3bbc1"/>',
        '<path class="ssd-press" d="', path, '" fill="#000"/>',
        '</g>',
      ].join(""), live));
    });
    return out.join("");
  }

  function render(container, options) {
    if (!container) throw new Error("SeedSignerDevice.render needs a container element");
    var o = options || {};
    var screenH = o.screenHeight > 0 ? o.screenHeight : 240;
    var scale = o.scale > 0 ? o.scale : 2;
    var live = o.interactive !== false;
    var withCard = o.card !== false;
    var onKey = typeof o.onKey === "function" ? o.onKey : null;

    injectStyle();
    var id = "ssd" + (++instances);   // gradients and filters must not collide
    var L = layout(screenH, scale, withCard);

    var svg = [
      '<svg class="ssd-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ',
      n(L.viewW), " ", n(L.viewH), '" preserveAspectRatio="xMidYMid meet" role="img"',
      live ? "" : ' aria-hidden="true"', ">",
      "<title>JikKey hardware wallet</title>",
      defs(id, L),
      withCard ? cardArt(id, L) : "",
      bodyArt(id, L),
      screenArt(id, L),
      screwArt(id, L),
      padArt(id, L, live),
      keysArt(id, L, live),
      "</svg>",
    ].join("");

    // Percentages, not pixels: the slot has to keep registration with the art no
    // matter what width the page gives us. Pixel offsets were why the canvas
    // walked off the shell on a phone.
    var slotStyle = "left:" + pct(L.screenX, L.viewW) + ";top:" + pct(L.screenY, L.viewH) +
      ";width:" + pct(L.sw, L.viewW) + ";height:" + pct(L.sh, L.viewH) +
      ";border-radius:0";
    // Glass last and inert: it must never eat a click or hide the wallet's pixels.
    var glassStyle = slotStyle +
      ";background:linear-gradient(125deg,rgba(255,255,255,.025),transparent 45%)";

    container.innerHTML = svg +
      '<div class="ssd-screen-slot" style="' + slotStyle + '"></div>' +
      '<div class="ssd-glass" style="' + glassStyle + '"></div>';
    container.classList.add("ssd-root");
    container.classList.toggle("ssd-live", live);
    // The natural width has to be a real length: the front page measures this
    // container with width:max-content before scaling it.
    container.style.width = n(L.viewW) + "px";
    // A landscape shell handed a whole desktop viewport is far wider than anyone
    // wants, so callers can cap it; either way it still shrinks to fit a phone.
    container.style.maxWidth = o.maxWidth ? "min(" + o.maxWidth + ",100%)" : "100%";
    // The shell's own proportions, published for a page that wants to fit it to
    // a viewport rather than only to a width.
    container.style.setProperty("--ssd-aspect", (L.viewW / L.viewH).toFixed(6));

    var svgEl = container.querySelector(".ssd-svg");
    var slotEl = container.querySelector(".ssd-screen-slot");
    // The screen is not a control. It used to be the select key, on the grounds
    // that it is the biggest target on the shell, and it surprised everybody who
    // touched it: on the home menu a tap anywhere opened the camera. A
    // SeedSigner has no touchscreen, so only the drawn keys answer here either.
    if (live && onKey) bindControls(svgEl, onKey);

    return {
      svg: svgEl,
      screen: slotEl,
      screenRect: { x: n(L.screenX), y: n(L.screenY), width: n(L.sw), height: n(L.sh) },
      width: n(L.viewW),
      height: n(L.viewH),
    };
  }

  global.SeedSignerDevice = { render: render, CHANNEL: CHANNEL };
})(typeof window !== "undefined" ? window : this);
