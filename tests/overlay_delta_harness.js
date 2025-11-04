const fs = require("fs");
const path = require("path");
const vm = require("vm");

const overlayPath = path.resolve(__dirname, "../overlay/overlay.js");
const overlaySource = fs.readFileSync(overlayPath, "utf8");

const noop = () => {};
const stubContext = {
  save: noop,
  restore: noop,
  setTransform: noop,
  clearRect: noop,
  scale: noop,
  beginPath: noop,
  moveTo: noop,
  lineTo: noop,
  quadraticCurveTo: noop,
  closePath: noop,
  fill: noop,
  stroke: noop,
  arc: noop,
  setLineDash: noop,
  fillRect: noop,
  fillText: noop,
  strokeText: noop,
  translate: noop,
  lineWidth: 1,
  font: "",
  textAlign: "",
  textBaseline: "",
  strokeStyle: "",
  fillStyle: "",
};

const canvas = {
  getContext: () => stubContext,
  getBoundingClientRect: () => ({ width: 1920, height: 1080 }),
  addEventListener: noop,
  width: 1920,
  height: 1080,
};

const checkbox = { checked: true, addEventListener: noop };
const document = {
  getElementById(id) {
    switch (id) {
      case "overlay-canvas":
        return canvas;
      case "port":
        return { value: "", addEventListener: noop };
      case "connect":
        return { addEventListener: noop };
      case "status":
        return { textContent: "", className: "" };
      case "toggle-radar":
      case "toggle-progress":
      case "toggle-delta":
        return checkbox;
      default:
        return {};
    }
  },
};

const windowObj = {
  devicePixelRatio: 1,
  addEventListener: noop,
  removeEventListener: noop,
  location: { search: "" },
};

global.window = windowObj;
global.document = document;
global.requestAnimationFrame = (cb) => {
  cb();
  return 1;
};
global.cancelAnimationFrame = noop;
global.WebSocket = function WebSocket() {
  throw new Error("WebSocket should not be instantiated in tests");
};
global.performance = { now: () => Date.now() };

vm.runInThisContext(overlaySource, { filename: "overlay.js" });

const helpers = window.__overlayTest;
if (!helpers) {
  throw new Error("overlay helpers were not registered");
}

const { parseIncoming, formatDelta } = helpers;

const basePlayer = { position: { x: 0, y: 0 } };

const positiveMsState = parseIncoming({
  player: { ...basePlayer, delta_ms: 70000 },
});
const negativeMsState = parseIncoming({
  player: { ...basePlayer, delta_ms: -45000 },
});
const secondsState = parseIncoming({
  player: { ...basePlayer, delta: 10 },
});

const result = {
  positive: formatDelta(positiveMsState.player.delta),
  negative: formatDelta(negativeMsState.player.delta),
  seconds: formatDelta(secondsState.player.delta),
};

process.stdout.write(`${JSON.stringify(result)}\n`);
