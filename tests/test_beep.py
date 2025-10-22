"""Tests for the beep configuration and audio drivers."""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

from main import AppConfig, BeepConfig, BeepSubsystem
from src.audio import beep_driver
from src.outsim_client import OutSimFrame


def _base_config_dict() -> dict:
    return {
        "insim": {},
        "outsim": {},
        "telemetry_ws": {},
    }


def _make_frame(time_ms: int, speed: float) -> OutSimFrame:
    return OutSimFrame(
        time_ms=time_ms,
        ang_vel=(0.0, 0.0, 0.0),
        heading=(0.0, 0.0, 0.0),
        acceleration=(0.0, 0.0, 0.0),
        velocity=(speed, 0.0, 0.0),
        position=(0.0, 0.0, 0.0),
    )


class RecordingDriver:
    def __init__(self) -> None:
        self.enabled = False
        self.volume = None
        self.beep_calls: list[tuple[float, int]] = []

    def set_volume(self, volume: float) -> None:
        self.volume = volume

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def play_beep(self, frequency_hz: float, duration_ms: int) -> None:
        if not self.enabled:
            raise AssertionError("beep played while driver disabled")
        self.beep_calls.append((frequency_hz, duration_ms))


def test_app_config_parses_beep_section() -> None:
    raw = _base_config_dict()
    raw["beep"] = {
        "mode": "aggressive",
        "volume": 0.75,
        "base_frequency_hz": 990.0,
        "intervals_ms": [120, 240],
    }

    config = AppConfig.from_dict(raw)

    assert config.beep == BeepConfig(
        mode="aggressive",
        volume=0.75,
        base_frequency_hz=990.0,
        intervals_ms=[120, 240],
    )


def test_app_config_validates_beep_fields() -> None:
    raw = _base_config_dict()
    raw["beep"] = {"volume": 1.5}

    with pytest.raises(ValueError):
        AppConfig.from_dict(raw)

    raw = _base_config_dict()
    raw["beep"] = {"intervals_ms": [200, 0]}
    with pytest.raises(ValueError):
        AppConfig.from_dict(raw)


def test_select_beep_driver_prefers_simpleaudio(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_module = SimpleNamespace()

    def fake_play_buffer(*_args, **_kwargs):
        return None

    dummy_module.play_buffer = fake_play_buffer
    monkeypatch.setattr(beep_driver, "_import_simpleaudio", lambda: dummy_module)

    driver = beep_driver.select_beep_driver()
    assert isinstance(driver, beep_driver.SimpleAudioBeepDriver)


def test_select_beep_driver_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(beep_driver, "_import_simpleaudio", lambda: None)

    driver = beep_driver.select_beep_driver()
    assert isinstance(driver, beep_driver.SilentBeepDriver)


def test_beep_subsystem_process_frame() -> None:
    config = BeepConfig(mode="standard", volume=0.5, base_frequency_hz=660.0, intervals_ms=[100, 200])
    driver = RecordingDriver()
    subsystem = BeepSubsystem(config, driver=driver)

    subsystem.set_enabled(True)

    frames = [
        _make_frame(0, 0.0),
        _make_frame(50, 0.0),
        _make_frame(100, 10.0),
        _make_frame(250, 15.0),
        _make_frame(300, 20.0),
        _make_frame(400, 5.0),
    ]

    for frame in frames:
        subsystem.process_frame(frame)

    assert driver.volume == pytest.approx(0.5)
    assert len(driver.beep_calls) == 3

    freq1, dur1 = driver.beep_calls[0]
    assert dur1 == 50
    assert math.isclose(freq1, 660.0 * (1 + 10.0 / 50.0))

    freq2, dur2 = driver.beep_calls[1]
    assert dur2 == 100
    assert math.isclose(freq2, 660.0 * (1 + 20.0 / 50.0))

    freq3, dur3 = driver.beep_calls[2]
    assert dur3 == 50
    assert math.isclose(freq3, 660.0 * (1 + 5.0 / 50.0))
