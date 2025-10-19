"""Radar and audio cue coordination for the LFS-Ayats prototype.

This module centralises the runtime state that decides whether the radar HUD
and the spotter beeps are enabled.  Historically these flags were only stored in
``config.json`` which meant changing them required editing a file and
restarting the application.  The new InSim button workflow toggles the values
in memory, so the radar renderer and the audio layer need to react to live
updates instead of reading from configuration files only.

The :class:`RadarController` exposes a tiny event bus that other modules can
subscribe to.  Every state transition publishes a :class:`RadarState` object,
allowing the HUD renderer (or any other observer) to keep an up to date view of
what should be on screen and which sounds may play.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Iterable, List

__all__ = [
    "RadarController",
    "RadarEventBus",
    "RadarState",
]


@dataclass(frozen=True)
class RadarState:
    """Runtime switches that affect the ASCII HUD and the audio spotter.

    Attributes
    ----------
    radar_enabled:
        Whether the ASCII radar overlay should be rendered.  When ``False`` the
        renderer is expected to clear the HUD to make room for other widgets.
    beeps_enabled:
        Whether the spotter should play close-proximity beeps.  Guarding the
        sound effect here keeps the audio logic isolated from the UI layer.
    """

    radar_enabled: bool = True
    beeps_enabled: bool = True


class RadarEventBus:
    """Simple multicast bus that broadcasts :class:`RadarState` updates."""

    def __init__(self) -> None:
        self._listeners: List[Callable[[RadarState], None]] = []

    def subscribe(self, listener: Callable[[RadarState], None]) -> None:
        """Register ``listener`` to be called for every state update."""

        if listener in self._listeners:
            return
        self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[[RadarState], None]) -> None:
        """Remove ``listener`` from future notifications if it was registered."""

        try:
            self._listeners.remove(listener)
        except ValueError:
            # Removing a listener that is not on the list is a no-op on purpose.
            pass

    # Separate method to make testing of notify easier
    def listeners(self) -> Iterable[Callable[[RadarState], None]]:
        """Return an iterable over the currently subscribed listeners."""

        return tuple(self._listeners)

    def publish(self, state: RadarState) -> None:
        """Broadcast ``state`` to all listeners."""

        for listener in list(self._listeners):
            listener(state)


class RadarController:
    """Authoritative source of truth for radar and beep runtime state."""

    def __init__(self, event_bus: RadarEventBus | None = None) -> None:
        self._state = RadarState()
        self._bus = event_bus or RadarEventBus()

    # -- subscription helpers -------------------------------------------------
    def subscribe(
        self, listener: Callable[[RadarState], None], *, replay: bool = True
    ) -> None:
        """Register ``listener`` and immediately emit the current state.

        Parameters
        ----------
        listener:
            Callable that receives :class:`RadarState` objects.
        replay:
            When ``True`` (the default) the listener is immediately called with
            the current state so new subscribers can synchronise without waiting
            for the next toggle event.
        """

        self._bus.subscribe(listener)
        if replay:
            listener(self._state)

    def unsubscribe(self, listener: Callable[[RadarState], None]) -> None:
        """Remove ``listener`` from the event bus."""

        self._bus.unsubscribe(listener)

    # -- state accessors ------------------------------------------------------
    @property
    def state(self) -> RadarState:
        """Expose the current :class:`RadarState`."""

        return self._state

    def is_radar_enabled(self) -> bool:
        return self._state.radar_enabled

    def are_beeps_enabled(self) -> bool:
        return self._state.beeps_enabled

    # -- mutations ------------------------------------------------------------
    def set_radar_enabled(self, enabled: bool) -> None:
        """Toggle the radar HUD and publish the new state."""

        if enabled == self._state.radar_enabled:
            return
        self._update_state(replace(self._state, radar_enabled=enabled))

    def set_beeps_enabled(self, enabled: bool) -> None:
        """Toggle the audio beeps and publish the new state."""

        if enabled == self._state.beeps_enabled:
            return
        self._update_state(replace(self._state, beeps_enabled=enabled))

    def _update_state(self, state: RadarState) -> None:
        self._state = state
        self._bus.publish(self._state)

    # -- behaviour helpers ----------------------------------------------------
    def maybe_render_ascii(self, ascii_renderer: Callable[[], str]) -> str:
        """Render the ASCII radar only if the feature is enabled.

        ``ascii_renderer`` is called lazily, avoiding unnecessary work when the
        radar HUD is hidden.
        """

        if not self._state.radar_enabled:
            return ""
        return ascii_renderer()

    def play_beep(self, play_callback: Callable[[], None]) -> bool:
        """Execute ``play_callback`` if spotter beeps are enabled.

        Returns ``True`` when the callback was invoked.  The caller can use this
        to log or drive counters during testing without talking to audio APIs.
        """

        if not self._state.beeps_enabled:
            return False
        play_callback()
        return True
