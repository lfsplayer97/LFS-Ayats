"""Simple HUD controller for drawing toggle buttons via InSim."""

from __future__ import annotations

import logging
from typing import Optional

from .insim_client import ISB_CLICK, InSimClient

logger = logging.getLogger(__name__)


class HUDController:
    """Manage a pair of toggle buttons rendered with InSim packets."""

    RADAR_BUTTON_ID = 200
    BEEPS_BUTTON_ID = 201

    def __init__(self, insim: InSimClient) -> None:
        self._insim = insim
        self._visible = False
        self._radar_enabled = False
        self._beeps_enabled = False
        self._radar_summary: Optional[str] = None

    def show(
        self,
        radar_enabled: bool,
        beeps_enabled: bool,
        radar_summary: Optional[str] = None,
    ) -> None:
        """Display the HUD buttons with the supplied states."""

        self._radar_enabled = radar_enabled
        self._beeps_enabled = beeps_enabled
        self._radar_summary = self._clean_summary(radar_summary)
        self._visible = True
        self._draw_buttons()

    def update(
        self,
        radar_enabled: bool,
        beeps_enabled: bool,
        radar_summary: Optional[str] = None,
    ) -> None:
        """Refresh button captions to reflect the latest states."""

        self._radar_enabled = radar_enabled
        self._beeps_enabled = beeps_enabled
        self._radar_summary = self._clean_summary(radar_summary)
        if not self._visible:
            self._visible = True
        self._draw_buttons()

    def remove(self) -> None:
        """Remove the HUD buttons if they are currently shown."""

        if not self._visible:
            return

        self._visible = False
        try:
            self._insim.delete_button(button_id=self.RADAR_BUTTON_ID)
            self._insim.delete_button(button_id=self.BEEPS_BUTTON_ID)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to delete HUD buttons")

    def _draw_buttons(self) -> None:
        if not getattr(self._insim, "connected", True):
            logger.debug("Skipping HUD draw request: InSim connection not active")
            return

        radar_caption = self._build_radar_caption()
        beeps_caption = f"Beeps: {'ON' if self._beeps_enabled else 'OFF'}"

        try:
            self._insim.show_button(
                button_id=self.RADAR_BUTTON_ID,
                text=radar_caption,
                left=5,
                top=150,
                width=35,
                height=6,
                style=ISB_CLICK,
            )
            self._insim.show_button(
                button_id=self.BEEPS_BUTTON_ID,
                text=beeps_caption,
                left=45,
                top=150,
                width=35,
                height=6,
                style=ISB_CLICK,
            )
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to draw HUD buttons")

    def _clean_summary(self, summary: Optional[str]) -> Optional[str]:
        if summary is None:
            return None

        text = summary.strip()
        if not text:
            return None

        encoded = text.encode("latin-1", errors="ignore")[:200]
        cleaned = encoded.decode("latin-1", errors="ignore").strip()
        return cleaned or None

    def _build_radar_caption(self) -> str:
        if not self._radar_enabled:
            return "Radar: OFF"

        if self._radar_summary:
            return f"Radar: {self._radar_summary}"

        return "Radar: ON"
