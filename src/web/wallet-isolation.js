// Static hosts such as GitHub Pages cannot set COOP/COEP response headers.
// The existing same-origin service worker supplies them before wallet boot.
(function (global) {
  "use strict";
  const attemptsKey = "jikkey-isolation:" + location.pathname;

  function report(message, failed = false) {
    const status = document.getElementById("status");
    status.textContent = global.JikKeyI18n ? JikKeyI18n.t(message) : message;
    status.className = failed ? "err" : "";
  }

  function storage(value) {
    try {
      if (value === undefined) return Number(sessionStorage.getItem(attemptsKey) || 0);
      if (value === 0) sessionStorage.removeItem(attemptsKey);
      else sessionStorage.setItem(attemptsKey, String(value));
      return value;
    } catch (_) {
      // Without a reload marker we cannot guarantee a finite retry count.
      return null;
    }
  }

  function activated(worker) {
    if (!worker || worker.state === "activated") return Promise.resolve();
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => finish(new Error("activation timeout")), 20000);
      function finish(error) {
        clearTimeout(timer);
        worker.removeEventListener("statechange", changed);
        error ? reject(error) : resolve();
      }
      function changed() {
        if (worker.state === "activated") finish();
        else if (worker.state === "redundant") finish(new Error("worker replaced"));
      }
      worker.addEventListener("statechange", changed);
      changed();
    });
  }

  async function ready() {
    if (global.crossOriginIsolated && typeof SharedArrayBuffer !== "undefined") {
      storage(0);
      if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
      return true;
    }
    if (!global.isSecureContext) {
      report("Open the HTTPS address to run the simulator on your phone.", true);
      return false;
    }
    if (!("serviceWorker" in navigator) || storage() === null || storage() >= 2) {
      report("This browser could not start the simulator. Open this page in a regular browser tab and try again.", true);
      return false;
    }
    report("Preparing the simulator. This page will refresh once.");
    try {
      const registration = await navigator.serviceWorker.register("sw.js");
      await activated(registration.installing || registration.waiting);
      await navigator.serviceWorker.ready;
      storage(storage() + 1);
      location.reload();
    } catch (_) {
      report("This browser could not start the simulator. Open this page in a regular browser tab and try again.", true);
    }
    return false;
  }

  global.SimulatorIsolation = { ready };
})(window);
