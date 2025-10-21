(() => {
  const canvas = document.getElementById("overlay-canvas");
  const ctx = canvas.getContext("2d");
  const portInput = document.getElementById("port");
  const connectBtn = document.getElementById("connect");
  const statusEl = document.getElementById("status");
  const toggleRadar = document.getElementById("toggle-radar");
  const toggleProgress = document.getElementById("toggle-progress");
  const toggleDelta = document.getElementById("toggle-delta");

  const toggles = {
    radar: toggleRadar.checked,
    progress: toggleProgress.checked,
    delta: toggleDelta.checked,
  };

  let socket = null;
  let lastMessageAt = 0;
  let latestState = null;
  let animationFrame = null;

  function getCanvasSize() {
    const rect = canvas.getBoundingClientRect();
    return { width: rect.width, height: rect.height };
  }

  function clearCanvas() {
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.restore();
  }

  function setStatus(text, className) {
    statusEl.textContent = text;
    statusEl.className = className;
  }

  function resizeCanvas() {
    const ratio = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.round(rect.width * ratio);
    canvas.height = Math.round(rect.height * ratio);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(ratio, ratio);
    draw();
  }

  function normalizeHeading(value) {
    if (typeof value !== "number" || Number.isNaN(value)) {
      return 0;
    }
    if (Math.abs(value) > Math.PI * 2) {
      return (value * Math.PI) / 180;
    }
    return value;
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function extract2DPosition(entity) {
    if (!entity || typeof entity !== "object") {
      return { x: 0, y: 0 };
    }
    const candidates = [
      ["x", "z"],
      ["X", "Z"],
      ["posX", "posZ"],
      ["pos_x", "pos_z"],
      ["posX", "posY"],
      ["x", "y"],
      ["X", "Y"],
    ];
    for (const [a, b] of candidates) {
      if (typeof entity[a] === "number" && typeof entity[b] === "number") {
        return { x: entity[a], y: entity[b] };
      }
    }
    if (entity.pos && typeof entity.pos === "object") {
      const { x = 0, y = 0, z = 0 } = entity.pos;
      return { x, y: z || y };
    }
    if (Array.isArray(entity.position) && entity.position.length >= 2) {
      return { x: entity.position[0], y: entity.position[1] };
    }
    return { x: 0, y: 0 };
  }

  function readNumber(entity, keys, fallback = 0) {
    if (!entity) return fallback;
    for (const key of keys) {
      if (typeof entity[key] === "number" && !Number.isNaN(entity[key])) {
        return entity[key];
      }
    }
    return fallback;
  }

  function readLapProgress(player, data) {
    const candidate = readNumber(
      player,
      ["lapProgress", "lap_progress", "lapFraction", "lap_fraction"],
      NaN,
    );
    if (Number.isFinite(candidate)) {
      return clamp(candidate <= 1 ? candidate : candidate / 100, 0, 1);
    }
    const percent = readNumber(player, ["lapPercent", "lap_percent"], NaN);
    if (Number.isFinite(percent)) {
      return clamp(percent <= 1 ? percent : percent / 100, 0, 1);
    }
    const lapData = data?.lap;
    const lapCandidate = readNumber(lapData, ["progress", "fraction"], NaN);
    if (Number.isFinite(lapCandidate)) {
      return clamp(lapCandidate <= 1 ? lapCandidate : lapCandidate / 100, 0, 1);
    }
    const lapPercent = readNumber(lapData, ["percent", "pct"], NaN);
    if (Number.isFinite(lapPercent)) {
      return clamp(lapPercent <= 1 ? lapPercent : lapPercent / 100, 0, 1);
    }
    return 0;
  }

  function formatDelta(deltaSeconds) {
    if (!Number.isFinite(deltaSeconds)) {
      return "--";
    }
    const sign = deltaSeconds > 0 ? "+" : "";
    const abs = Math.abs(deltaSeconds);
    const minutes = Math.floor(abs / 60);
    const seconds = abs % 60;
    const formatted = `${minutes ? minutes + ":" : ""}${seconds.toFixed(3).padStart(minutes ? 6 : 4, "0")}`;
    return `${sign}${formatted}`;
  }

  function parseIncoming(data) {
    if (!data) {
      return null;
    }
    const player = data.player || data.car || data.local || null;
    const mci = data.mci || data.cars || data.vehicles || [];

    const { x: px, y: py } = extract2DPosition(player || {});
    const heading = normalizeHeading(
      readNumber(player, ["heading", "Heading", "yaw", "Yaw", "dir", "direction"], 0),
    );
    const lapProgress = readLapProgress(player, data);
    let delta = readNumber(
      player,
      ["delta", "deltaLap", "deltaCurrent", "lapDelta", "splitDelta"],
      readNumber(data.delta, ["current", "lap", "value"], NaN),
    );
    if (Math.abs(delta) > 30 && Math.abs(delta) < 60000) {
      delta = delta / 1000;
    }

    let entries = [];
    if (Array.isArray(mci)) {
      entries = mci;
    } else if (mci && typeof mci === "object") {
      entries = Object.values(mci);
    }
    const cars = entries
      .map((entry) => {
        const { x, y } = extract2DPosition(entry);
        const relX = x - px;
        const relY = y - py;
        const distance = Math.hypot(relX, relY);
        const name = entry.name || entry.driver || entry.id || entry.PLID || "car";
        return { relX, relY, distance, name };
      })
      .filter((c) => Number.isFinite(c.distance) && c.distance > 0.5);

    return { player: { px, py, heading, lapProgress, delta }, cars };
  }

  function drawRadar(state) {
    const { width, height } = getCanvasSize();
    const radarRadius = Math.min(width, height) * 0.35;
    const centerX = Math.min(radarRadius + 40, width * 0.4);
    const centerY = height * 0.55;
    const maxRange = 140;
    const scale = radarRadius / maxRange;
    const cosH = Math.cos(state.player.heading);
    const sinH = Math.sin(state.player.heading);

    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.fillStyle = "rgba(15, 23, 42, 0.55)";
    ctx.strokeStyle = "rgba(148, 163, 184, 0.35)";
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.arc(0, 0, radarRadius, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    ctx.lineWidth = 1;
    ctx.setLineDash([6, 6]);
    for (let ring = radarRadius / 3; ring < radarRadius; ring += radarRadius / 3) {
      ctx.beginPath();
      ctx.arc(0, 0, ring, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.setLineDash([]);

    // Draw heading lines
    ctx.strokeStyle = "rgba(148, 163, 184, 0.25)";
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, -radarRadius);
    ctx.stroke();

    // Player car
    ctx.fillStyle = "#22d3ee";
    ctx.beginPath();
    ctx.moveTo(0, -16);
    ctx.lineTo(8, 12);
    ctx.lineTo(-8, 12);
    ctx.closePath();
    ctx.fill();

    // Opponents
    for (const car of state.cars) {
      const rotatedX = car.relX * cosH - car.relY * sinH;
      const rotatedY = car.relX * sinH + car.relY * cosH;
      const x = clamp(rotatedX * scale, -radarRadius, radarRadius);
      const y = clamp(-rotatedY * scale, -radarRadius, radarRadius);
      const opacity = clamp(1 - car.distance / maxRange, 0.2, 0.9);
      ctx.fillStyle = `rgba(248, 113, 113, ${opacity.toFixed(2)})`;
      ctx.beginPath();
      ctx.arc(x, y, 6, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();
  }

  function drawRoundedRect(x, y, width, height, radius) {
    const r = Math.min(radius, height / 2, width / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + width - r, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + r);
    ctx.lineTo(x + width, y + height - r);
    ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
    ctx.lineTo(x + r, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  function drawLapProgress(state) {
    const { width, height } = getCanvasSize();
    const barWidth = width * 0.8;
    const barHeight = 24;
    const x = (width - barWidth) / 2;
    const y = height - barHeight - 24;

    ctx.save();
    ctx.fillStyle = "rgba(15, 23, 42, 0.7)";
    ctx.strokeStyle = "rgba(148, 163, 184, 0.45)";
    ctx.lineWidth = 2;
    drawRoundedRect(x, y, barWidth, barHeight, 12);
    ctx.fill();
    ctx.stroke();

    const progress = clamp(state.player.lapProgress || 0, 0, 1);
    ctx.fillStyle = "rgba(79, 209, 197, 0.85)";
    if (progress > 0) {
      drawRoundedRect(x + 3, y + 3, (barWidth - 6) * progress, barHeight - 6, 9);
      ctx.fill();
    }

    ctx.fillStyle = "rgba(226, 232, 240, 0.8)";
    ctx.font = "16px 'Inter', 'Segoe UI', sans-serif";
    ctx.textBaseline = "middle";
    ctx.textAlign = "center";
    ctx.fillText(`${Math.round(progress * 100)}%`, x + barWidth / 2, y + barHeight / 2);
    ctx.restore();
  }

  function drawDelta(state) {
    const { width } = getCanvasSize();
    const x = width - 32;
    const y = 48;
    const deltaValue = state.player.delta;
    const hasDelta = Number.isFinite(deltaValue);
    const isPositive = hasDelta && deltaValue > 0;

    ctx.save();
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    ctx.font = "28px 'Inter', 'Segoe UI', sans-serif";
    ctx.fillStyle = hasDelta
      ? isPositive
        ? "rgba(248, 113, 113, 0.9)"
        : "rgba(52, 211, 153, 0.9)"
      : "rgba(148, 163, 184, 0.8)";
    ctx.strokeStyle = "rgba(2, 6, 23, 0.65)";
    ctx.lineWidth = 4;
    const deltaText = formatDelta(deltaValue);
    ctx.strokeText(deltaText, x, y);
    ctx.fillText(deltaText, x, y);
    ctx.restore();
  }

  function drawFallback(message) {
    const { width, height } = getCanvasSize();
    clearCanvas();
    ctx.save();
    ctx.fillStyle = "rgba(15, 23, 42, 0.65)";
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = "rgba(226, 232, 240, 0.9)";
    ctx.font = "20px 'Inter', 'Segoe UI', sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(message, width / 2, height / 2);
    ctx.restore();
  }

  function draw() {
    cancelAnimationFrame(animationFrame);
    animationFrame = requestAnimationFrame(() => {
      clearCanvas();
      if (!latestState) {
        drawFallback("Waiting for telemetry…");
        return;
      }
      if (Date.now() - lastMessageAt > 2500) {
        drawFallback("Telemetry paused");
        return;
      }
      if (toggles.radar) {
        drawRadar(latestState);
      }
      if (toggles.progress) {
        drawLapProgress(latestState);
      }
      if (toggles.delta) {
        drawDelta(latestState);
      }
    });
  }

  function teardownSocket() {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.close(1000, "client navigating");
    }
    socket = null;
  }

  function connect() {
    const port = Number.parseInt(portInput.value, 10);
    if (!Number.isInteger(port) || port < 1 || port > 65535) {
      setStatus("Invalid", "status--error");
      return;
    }
    teardownSocket();
    setStatus("Connecting", "status--connecting");

    try {
      socket = new WebSocket(`ws://127.0.0.1:${port}`);
    } catch (err) {
      console.error("WebSocket error", err);
      setStatus("Error", "status--error");
      return;
    }

    socket.addEventListener("open", () => {
      setStatus("Connected", "status--connected");
    });

    socket.addEventListener("message", (event) => {
      try {
        const payload = JSON.parse(event.data);
        const parsed = parseIncoming(payload);
        if (parsed) {
          latestState = parsed;
          lastMessageAt = Date.now();
          draw();
        }
      } catch (err) {
        console.warn("Could not parse telemetry", err);
      }
    });

    socket.addEventListener("close", () => {
      setStatus("Disconnected", "status--disconnected");
      latestState = null;
      drawFallback("Socket closed – retry?");
    });

    socket.addEventListener("error", (event) => {
      console.error("WebSocket error", event);
      setStatus("Error", "status--error");
    });
  }

  connectBtn.addEventListener("click", connect);

  portInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      connect();
    }
  });

  toggleRadar.addEventListener("change", (event) => {
    toggles.radar = event.target.checked;
    draw();
  });

  toggleProgress.addEventListener("change", (event) => {
    toggles.progress = event.target.checked;
    draw();
  });

  toggleDelta.addEventListener("change", (event) => {
    toggles.delta = event.target.checked;
    draw();
  });

  window.addEventListener("resize", resizeCanvas);
  window.addEventListener("beforeunload", teardownSocket);

  resizeCanvas();

  // Auto-connect if the port is supplied via query string (?port=49100)
  const params = new URLSearchParams(window.location.search);
  if (params.has("port")) {
    const queryPort = params.get("port");
    if (queryPort) {
      portInput.value = queryPort;
    }
    connect();
  }
})();
