"""
Streaming Overlay Integration
Real-time telemetry overlay for OBS and streaming platforms
"""

from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO
from typing import Dict, Any, Optional
import threading


# HTML template for overlay
OVERLAY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LFS Telemetry Overlay</title>
    <meta charset="utf-8">
    <style>
        body {
            margin: 0;
            background: transparent;
            font-family: 'Arial', sans-serif;
            overflow: hidden;
        }
        .telemetry {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            min-width: 200px;
        }
        .speed {
            font-size: 48px;
            font-weight: bold;
            color: #00ff00;
            text-align: center;
            margin-bottom: 10px;
        }
        .rpm {
            font-size: 24px;
            color: #ff6b6b;
            text-align: center;
            margin-bottom: 8px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-size: 16px;
        }
        .label {
            color: #aaa;
        }
        .value {
            font-weight: bold;
        }
        .lap-time {
            font-size: 20px;
            text-align: center;
            margin-top: 10px;
            color: #ffd700;
        }
    </style>
</head>
<body>
    <div class="telemetry">
        <div class="speed" id="speed">0 km/h</div>
        <div class="rpm" id="rpm">0 RPM</div>
        <div class="info-row">
            <span class="label">Gear:</span>
            <span class="value" id="gear">N</span>
        </div>
        <div class="info-row">
            <span class="label">Position:</span>
            <span class="value" id="position">-</span>
        </div>
        <div class="lap-time" id="lap-time">00:00.000</div>
    </div>

    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script>
        const socket = io();

        socket.on('telemetry_update', (data) => {
            // Update speed
            document.getElementById('speed').innerText =
                `${Math.round(data.speed || 0)} km/h`;

            // Update RPM
            document.getElementById('rpm').innerText =
                `${Math.round(data.rpm || 0)} RPM`;

            // Update gear
            const gear = data.gear || 'N';
            document.getElementById('gear').innerText = gear;

            // Update position
            const position = data.position || '-';
            document.getElementById('position').innerText = position;

            // Update lap time
            if (data.lap_time !== undefined) {
                document.getElementById('lap-time').innerText =
                    formatTime(data.lap_time);
            }
        });

        function formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${mins.toString().padStart(2, '0')}:${secs.toFixed(3).padStart(6, '0')}`;
        }

        socket.on('connect', () => {
            console.log('Connected to telemetry server');
        });

        socket.on('disconnect', () => {
            console.log('Disconnected from telemetry server');
        });
    </script>
</body>
</html>
"""


class StreamingOverlay:
    """
    Real-time telemetry overlay for streaming platforms.

    This class provides a web server that serves an HTML overlay
    compatible with OBS Browser Source, displaying real-time telemetry
    data via WebSocket connections.

    Args:
        port: Port to run the overlay server on (default: 5000)
        host: Host address to bind to (default: '0.0.0.0')
        debug: Enable Flask debug mode (default: False)

    Example:
        >>> overlay = StreamingOverlay(port=5000)
        >>> overlay.start()  # Start in background thread
        >>> # Later, update telemetry data
        >>> overlay.update_telemetry({
        ...     'speed': 120.5,
        ...     'rpm': 6500,
        ...     'gear': 4,
        ...     'lap_time': 98.456
        ... })

    Usage with OBS:
        1. Add "Browser" source to OBS scene
        2. Set URL to: http://localhost:5000
        3. Set Width: 1920, Height: 1080
        4. Enable "Shutdown source when not visible"
        5. Adjust position and size as needed
    """

    def __init__(self, port: int = 5000, host: str = "0.0.0.0", debug: bool = False):
        """
        Initialize streaming overlay.

        Args:
            port: Port number for the server
            host: Host address to bind to
            debug: Enable debug mode
        """
        self.port = port
        self.host = host
        self.debug = debug
        self.current_data: Dict[str, Any] = {}

        # Initialize Flask app and SocketIO
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "lfs-ayats-overlay-secret"
        self.socketio = SocketIO(
            self.app, cors_allowed_origins="*", async_mode="threading"
        )

        # Setup routes
        self._setup_routes()

        # Server thread
        self._server_thread: Optional[threading.Thread] = None
        self._running = False

    def _setup_routes(self):
        """Setup Flask routes."""

        @self.app.route("/")
        def index():
            """Serve the overlay HTML page."""
            return render_template_string(OVERLAY_TEMPLATE)

        @self.app.route("/api/telemetry")
        def get_telemetry():
            """Get current telemetry data as JSON."""
            return jsonify(self.current_data)

        @self.app.route("/health")
        def health():
            """Health check endpoint."""
            return jsonify({"status": "ok", "running": self._running})

    def update_telemetry(self, telemetry_data: Dict[str, Any]) -> None:
        """
        Update telemetry data and broadcast to connected clients.

        Args:
            telemetry_data: Dictionary containing telemetry information
                - speed: Speed in km/h
                - rpm: Engine RPM
                - gear: Current gear (0-6, N for neutral)
                - lap_time: Current lap time in seconds
                - position: Current position (optional)

        Example:
            >>> overlay.update_telemetry({
            ...     'speed': 120.5,
            ...     'rpm': 6500,
            ...     'gear': 4,
            ...     'lap_time': 98.456,
            ...     'position': '2/10'
            ... })
        """
        self.current_data.update(telemetry_data)

        # Broadcast to all connected clients
        if self._running:
            self.socketio.emit("telemetry_update", telemetry_data)

    def start(self) -> None:
        """
        Start the overlay server in a background thread.

        The server will run in a separate thread to avoid blocking
        the main application.

        Example:
            >>> overlay = StreamingOverlay(port=5000)
            >>> overlay.start()
            >>> print("Server started in background")
        """
        if self._running:
            print("Overlay server already running")
            return

        self._running = True

        def run_server():
            """Run the SocketIO server."""
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=self.debug,
                use_reloader=False,
            )

        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()

        print(f"Streaming overlay started at http://{self.host}:{self.port}")

    def stop(self) -> None:
        """
        Stop the overlay server.

        Note: Due to Flask/SocketIO limitations, the server cannot be
        cleanly stopped without restarting the application.
        """
        self._running = False
        print("Overlay server stopped (thread may still be running)")

    def is_running(self) -> bool:
        """
        Check if the overlay server is running.

        Returns:
            True if server is running, False otherwise
        """
        return self._running
