// Touch assistance belongs to the simulator, not the physical device art.
// Hardware buttons and desktop mouse input keep their existing behavior.
(function (global) {
  "use strict";
  const TOUCH = 1 << 30;

  function mount(canvas, { frame, send }) {
    let gesture = null;

    function point(event) {
      const bounds = canvas.getBoundingClientRect();
      const u = (event.clientX - bounds.left) / bounds.width;
      const v = (event.clientY - bounds.top) / bounds.height;
      const rotated = document.body.classList.contains("solo") &&
        matchMedia("(orientation: portrait)").matches;
      return rotated ? { x: v, y: 1 - u } : { x: u, y: v };
    }

    canvas.addEventListener("pointerdown", (event) => {
      if (event.pointerType !== "touch" || !event.isPrimary) {
        if (event.pointerType === "touch") gesture = null;
        return;
      }
      const state = frame();
      if (state.epoch === null) return;
      event.preventDefault();
      gesture = { id: event.pointerId, point: point(event), state,
        clientX: event.clientX, clientY: event.clientY, moved: false };
      canvas.setPointerCapture(event.pointerId);
    });

    canvas.addEventListener("pointermove", (event) => {
      if (!gesture || gesture.id !== event.pointerId) return;
      if (Math.hypot(event.clientX - gesture.clientX, event.clientY - gesture.clientY) > 12) {
        gesture.moved = true;
      }
    });

    canvas.addEventListener("pointerup", (event) => {
      if (!gesture || gesture.id !== event.pointerId) return;
      const start = gesture;
      gesture = null;
      event.preventDefault();
      if (frame().epoch !== start.state.epoch) return;
      const end = point(event);
      if (end.x < 0 || end.x >= 1 || end.y < 0 || end.y >= 1) return;
      const dx = end.x - start.point.x, dy = end.y - start.point.y;
      if (start.moved) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) < .14) return;
        // A vertical swipe moves through a menu; horizontal swipes are the
        // existing left/right buttons. Never synthesize an activation here.
        const channel = Math.abs(dy) >= Math.abs(dx) ? (dy < 0 ? 2 : 1) : (dx < 0 ? 3 : 4);
        send(TOUCH | (start.state.epoch << 18) | (511 << 9) | channel);
        return;
      }
      const x = Math.floor(end.x * start.state.width);
      const y = Math.floor(end.y * start.state.height);
      if (x > 511 || y > 511) return;
      send(TOUCH | (start.state.epoch << 18) | (y << 9) | x);
    });

    for (const event of ["pointercancel", "lostpointercapture"]) {
      canvas.addEventListener(event, () => { gesture = null; });
    }
  }

  global.WalletTouch = { mount };
})(window);
