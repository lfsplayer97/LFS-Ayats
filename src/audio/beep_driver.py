"""Audio driver selection utilities for the beep subsystem."""

from __future__ import annotations

import logging
import math
from array import array
from types import ModuleType
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class BeepDriver(Protocol):
    """Minimal interface implemented by beep audio backends."""

    def set_volume(self, volume: float) -> None:
        """Update the playback volume in the range ``[0.0, 1.0]``."""

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable playback on the backend."""

    def play_beep(self, frequency_hz: float, duration_ms: int) -> None:
        """Play a tone with the requested frequency and duration."""


def _import_simpleaudio() -> ModuleType | None:
    try:
        import simpleaudio  # type: ignore[import]
    except Exception:  # pragma: no cover - defensive
        return None
    return simpleaudio


class SimpleAudioBeepDriver:
    """Play sine-wave tones using the :mod:`simpleaudio` package."""

    _SAMPLE_RATE = 44100

    def __init__(self, module: ModuleType | None = None) -> None:
        if module is None:
            module = _import_simpleaudio()
        if module is None:
            raise RuntimeError("simpleaudio module not available")
        self._simpleaudio = module
        self._volume = 0.5
        self._enabled = False

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, float(volume)))

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    def play_beep(self, frequency_hz: float, duration_ms: int) -> None:
        if not self._enabled:
            return
        if self._volume <= 0.0:
            return
        if frequency_hz <= 0 or duration_ms <= 0:
            return

        duration_seconds = min(duration_ms / 1000.0, 2.0)
        sample_count = max(int(round(duration_seconds * self._SAMPLE_RATE)), 1)
        amplitude = int(round(32767 * self._volume))
        angular_velocity = 2.0 * math.pi * float(frequency_hz) / self._SAMPLE_RATE

        samples = array("h", (0 for _ in range(sample_count)))
        for index in range(sample_count):
            samples[index] = int(round(amplitude * math.sin(angular_velocity * index)))

        try:
            self._simpleaudio.play_buffer(samples.tobytes(), 1, 2, self._SAMPLE_RATE)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to play beep via simpleaudio")


class SilentBeepDriver:
    """Fallback driver that only logs the requested beeps."""

    def __init__(self) -> None:
        self._enabled = False
        self._volume = 0.0

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, float(volume)))

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    def play_beep(self, frequency_hz: float, duration_ms: int) -> None:
        if not self._enabled:
            return
        logger.debug(
            "Silent beep: frequency=%sHz duration=%sms volume=%s", frequency_hz, duration_ms, self._volume
        )


def select_beep_driver() -> BeepDriver:
    """Return the first usable beep driver implementation."""

    module = _import_simpleaudio()
    if module is not None:
        try:
            driver = SimpleAudioBeepDriver(module)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to initialise simpleaudio beep driver; falling back")
        else:
            logger.info("Using simpleaudio beep driver")
            return driver

    logger.info("Using silent beep driver")
    return SilentBeepDriver()


__all__ = [
    "BeepDriver",
    "SilentBeepDriver",
    "SimpleAudioBeepDriver",
    "select_beep_driver",
]
