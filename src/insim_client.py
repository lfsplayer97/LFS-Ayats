"""Lightweight InSim client with runtime toggle buttons."""

from __future__ import annotations

import logging
import socket
import struct
import threading
from dataclasses import dataclass
from typing import Callable, Optional

from .hud import HUDRenderer
from .radar import RadarController

__all__ = ["InSimClient", "InSimConfig", "BUTTON_BEEP_ID", "BUTTON_RADAR_ID"]

LOGGER = logging.getLogger(__name__)

# Packet type identifiers from the InSim protocol.
ISP_ISI = 1
ISP_BTN = 18
ISP_BTC = 19

BUTTON_RADAR_ID = 200
BUTTON_BEEP_ID = 201


@dataclass
class InSimConfig:
    """Connection configuration for the InSim client."""

    host: str = "127.0.0.1"
    port: int = 29999
    admin_password: str = ""
    interval_ms: int = 100
    prefix: bytes = b"AYTS"
    udp_port: int = 0
    flags: int = 0


class InSimClient:
    """InSim client that draws toggle buttons and keeps them in sync."""

    def __init__(
        self,
        config: InSimConfig,
        radar_controller: RadarController,
        hud: HUDRenderer,
        *,
        on_hud_redraw: Optional[Callable[[str], None]] = None,
    ) -> None:
        self._config = config
        self._radar = radar_controller
        self._hud = hud
        self._hud.add_redraw_listener(self._handle_hud_redraw)
        self._external_redraw = on_hud_redraw

        self._socket: Optional[socket.socket] = None
        self._recv_thread: Optional[threading.Thread] = None
        self._recv_buffer = bytearray()
        self._running = threading.Event()
        self._lock = threading.Lock()

        # Prime the HUD with the current labels.
        self._hud.redraw()

    # -- connection -----------------------------------------------------------
    def connect(self) -> None:
        """Connect to LFS and send the initial InSim packets."""

        LOGGER.info("Connecting to InSim at %s:%s", self._config.host, self._config.port)
        self._socket = socket.create_connection((self._config.host, self._config.port))
        self._socket.settimeout(0.25)
        self._running.set()

        self._send(self._build_isi_packet())
        self.draw_buttons()

        self._recv_thread = threading.Thread(target=self._recv_loop, name="insim-recv", daemon=True)
        self._recv_thread.start()

    def close(self) -> None:
        """Close the connection and stop the receive thread."""

        self._running.clear()
        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self._socket.close()
            self._socket = None
        if self._recv_thread is not None:
            self._recv_thread.join(timeout=0.5)
            self._recv_thread = None

    # -- HUD integration ------------------------------------------------------
    def _handle_hud_redraw(self, _state, ascii_hud: str) -> None:
        if self._external_redraw is not None:
            self._external_redraw(ascii_hud)

    # -- button drawing -------------------------------------------------------
    def draw_buttons(self) -> None:
        """(Re)draw the toggle buttons with their current state."""

        self._send(self._build_button_packet(BUTTON_RADAR_ID, self._hud.button_caption("radar"), top=20))
        self._send(self._build_button_packet(BUTTON_BEEP_ID, self._hud.button_caption("beeps"), top=24))

    # -- packet builders ------------------------------------------------------
    def _build_isi_packet(self) -> bytes:
        """Build an :code:`IS_ISI` packet with the current configuration."""

        admin = self._config.admin_password.encode("latin-1", "ignore")[:15]
        admin = admin + b"\x00" * (16 - len(admin))
        iname = b"LFS-Ayats"[:15]
        iname = iname + b"\x00" * (16 - len(iname))
        prefix = (self._config.prefix or b"")[:4]
        prefix = prefix + b"\x00" * (4 - len(prefix))

        payload = struct.pack(
            "<BBBBHHH4s16s16s",
            0,  # placeholder for size filled later
            ISP_ISI,
            0,
            0,
            self._config.udp_port,
            self._config.flags,
            self._config.interval_ms,
            prefix,
            admin,
            iname,
        )
        size = len(payload)
        return bytes([size]) + payload[1:]

    def _build_button_packet(
        self,
        click_id: int,
        caption: str,
        *,
        left: int = 100,
        top: int = 20,
        width: int = 50,
        height: int = 12,
        inst: int = 0,
        bstyle: int = 0,
        type_in: int = 0,
    ) -> bytes:
        """Build an :code:`IS_BTN` packet for a labelled toggle button."""

        text = caption.encode("latin-1", "replace")[:239]
        text += b"\x00"
        header = struct.pack(
            "<BBBBBBBBBBBB",
            0,  # size placeholder
            ISP_BTN,
            0,
            0,
            click_id & 0xFF,
            inst & 0xFF,
            bstyle & 0xFF,
            type_in & 0xFF,
            left & 0xFF,
            top & 0xFF,
            width & 0xFF,
            height & 0xFF,
        )
        size = len(header) + len(text)
        return bytes([size]) + header[1:] + text

    # -- network loop ---------------------------------------------------------
    def _recv_loop(self) -> None:
        assert self._socket is not None
        while self._running.is_set():
            try:
                data = self._socket.recv(256)
            except socket.timeout:
                continue
            except OSError as exc:  # connection closed
                LOGGER.debug("InSim recv loop stopped: %s", exc)
                break
            if not data:
                break
            self._recv_buffer.extend(data)
            self._drain_buffer()

    def _drain_buffer(self) -> None:
        while len(self._recv_buffer) >= 2:
            size = self._recv_buffer[0]
            if len(self._recv_buffer) < size:
                return
            packet = bytes(self._recv_buffer[:size])
            del self._recv_buffer[:size]
            self._dispatch(packet)

    def _dispatch(self, packet: bytes) -> None:
        packet_type = packet[1]
        if packet_type == ISP_BTC:
            self._handle_btc(packet)

    # -- button event handling ------------------------------------------------
    def _handle_btc(self, packet: bytes) -> None:
        if len(packet) < 6:
            return
        click_id = packet[4]
        if click_id == (BUTTON_RADAR_ID & 0xFF):
            self._toggle_radar()
        elif click_id == (BUTTON_BEEP_ID & 0xFF):
            self._toggle_beeps()

    def _toggle_radar(self) -> None:
        new_state = not self._radar.is_radar_enabled()
        LOGGER.info("Radar toggle requested via InSim: %s", new_state)
        self._radar.set_radar_enabled(new_state)
        self.draw_buttons()

    def _toggle_beeps(self) -> None:
        new_state = not self._radar.are_beeps_enabled()
        LOGGER.info("Beeps toggle requested via InSim: %s", new_state)
        self._radar.set_beeps_enabled(new_state)
        self.draw_buttons()

    # -- low level send -------------------------------------------------------
    def _send(self, payload: bytes) -> None:
        if self._socket is None:
            raise RuntimeError("InSim connection not established")
        with self._lock:
            self._socket.sendall(payload)
