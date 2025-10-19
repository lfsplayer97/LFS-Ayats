"""ASCII HUD renderer helpers for the LFS-Ayats radar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from .radar import RadarController, RadarState

__all__ = [
    "HUDRenderer",
    "HUDState",
]


@dataclass(frozen=True)
class HUDState:
    """Snapshot of what should be drawn in the ASCII HUD."""

    radar_enabled: bool = True
    beeps_enabled: bool = True


class HUDRenderer:
    """Render the ASCII HUD and provide button labels for the InSim client."""

    def __init__(
        self,
        radar_controller: RadarController,
    ) -> None:
        self._radar_controller = radar_controller
        self._state = HUDState(
            radar_enabled=radar_controller.is_radar_enabled(),
            beeps_enabled=radar_controller.are_beeps_enabled(),
        )
        self._redraw_listeners: List[Callable[[HUDState, str], None]] = []
        radar_controller.subscribe(self._handle_radar_state)

    # -- subscription helpers -------------------------------------------------
    def add_redraw_listener(self, listener: Callable[[HUDState, str], None]) -> None:
        """Register ``listener`` to be called every time the HUD is redrawn."""

        if listener in self._redraw_listeners:
            return
        self._redraw_listeners.append(listener)

    def remove_redraw_listener(
        self, listener: Callable[[HUDState, str], None]
    ) -> None:
        """Remove ``listener`` from the redraw notification list."""

        try:
            self._redraw_listeners.remove(listener)
        except ValueError:
            pass

    # -- state handling -------------------------------------------------------
    def _handle_radar_state(self, state: RadarState) -> None:
        self._state = HUDState(
            radar_enabled=state.radar_enabled,
            beeps_enabled=state.beeps_enabled,
        )
        self.redraw()

    @property
    def state(self) -> HUDState:
        return self._state

    # -- rendering ------------------------------------------------------------
    def redraw(self) -> str:
        """Return the ASCII HUD representation and notify listeners."""

        ascii_hud = self.render()
        for listener in list(self._redraw_listeners):
            listener(self._state, ascii_hud)
        return ascii_hud

    def render(self) -> str:
        """Render the HUD as a multi-line ASCII string."""

        status_lines = [
            "┌────────────────────────┐",
            f"│ Radar : {'ON ' if self._state.radar_enabled else 'OFF'} │",
            f"│ Beeps : {'ON ' if self._state.beeps_enabled else 'OFF'} │",
            "└────────────────────────┘",
        ]
        return "\n".join(status_lines)

    # -- button helpers -------------------------------------------------------
    def button_caption(self, toggle: str) -> str:
        """Return a short caption for the requested toggle button."""

        if toggle == "radar":
            return "Radar: ON" if self._state.radar_enabled else "Radar: OFF"
        if toggle == "beeps":
            return "Beeps: ON" if self._state.beeps_enabled else "Beeps: OFF"
        raise ValueError(f"Unknown toggle '{toggle}'")
