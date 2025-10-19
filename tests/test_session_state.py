from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from main import clear_session_timing, update_session_best
from src.insim_client import LapEvent, StateEvent
from src.outsim_client import OutSimFrame
from src.persistence import PersonalBestRecord


def test_session_best_resets_with_context_change_and_rebuilds() -> None:
    lap_state = {
        "current_lap_start_ms": 1234,
        "best_lap_ms": 91000,
        "current_split_times": {1: 45000},
        "last_lap_split_fractions": [0.5],
        "pb_split_fractions": [0.3],
        "latest_estimated_total_ms": 92000,
    }

    clear_session_timing(lap_state)

    assert lap_state["best_lap_ms"] is None
    assert lap_state["current_lap_start_ms"] is None
    assert lap_state["current_split_times"] == {}
    assert lap_state["last_lap_split_fractions"] == []
    assert lap_state["pb_split_fractions"] == []
    assert lap_state["latest_estimated_total_ms"] is None

    assert update_session_best(lap_state, 90500) is True
    assert lap_state["best_lap_ms"] == 90500

    assert update_session_best(lap_state, 93000) is False
    assert lap_state["best_lap_ms"] == 90500

    clear_session_timing(lap_state)
    assert lap_state["best_lap_ms"] is None

    assert update_session_best(lap_state, 93000) is True
    assert lap_state["best_lap_ms"] == 93000


def test_handle_lap_switches_driver_after_track_change(monkeypatch) -> None:
    main_module = sys.modules["main"]
    record_calls: list[tuple[str, str, int]] = []

    class FakeInSimClient:
        events: list[tuple[str, object]] = []

        def __init__(
            self,
            config,
            *,
            state_listeners=None,
            lap_listeners=None,
            split_listeners=None,
        ) -> None:
            self._state_listeners = list(state_listeners or [])
            self._lap_listeners = list(lap_listeners or [])
            self._split_listeners = list(split_listeners or [])
            self._event_queue = list(self.events)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):  # type: ignore[override]
            return False

        def poll(self) -> None:
            if not self._event_queue:
                return

            kind, payload = self._event_queue.pop(0)
            if kind == "state":
                for callback in self._state_listeners:
                    callback(payload)
            elif kind == "lap":
                for callback in self._lap_listeners:
                    callback(payload)
            elif kind == "split":
                for callback in self._split_listeners:
                    callback(payload)

    class FakeOutSimClient:
        frames_to_yield: list[OutSimFrame] = []

        def __init__(self, port, host="0.0.0.0", buffer_size: int = 256, timeout=None) -> None:
            self._frames = list(self.frames_to_yield)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):  # type: ignore[override]
            return False

        def frames(self):
            yield from self._frames

    class DummyRadar:
        def draw(self, frame):
            pass

    def fake_record_lap(
        track: str,
        car: str,
        laptime_ms: int,
        *,
        timestamp=None,
        db_path=None,
    ):
        record_calls.append((track, car, laptime_ms))
        return (
            PersonalBestRecord(
                track=track,
                car=car,
                laptime_ms=laptime_ms,
                recorded_at=datetime.now(timezone.utc),
            ),
            True,
        )

    monkeypatch.setattr(main_module, "InSimClient", FakeInSimClient)
    monkeypatch.setattr(main_module, "OutSimClient", FakeOutSimClient)
    monkeypatch.setattr(main_module, "RadarRenderer", lambda: DummyRadar())
    monkeypatch.setattr(main_module, "load_personal_best", lambda track, car: None)
    monkeypatch.setattr(main_module, "record_lap", fake_record_lap)

    FakeInSimClient.events = [
        ("state", StateEvent(flags2=0, track="SO1", car="UF1")),
        (
            "lap",
            LapEvent(
                plid=5,
                lap_time_ms=0,
                estimate_time_ms=0,
                flags=0,
                penalty=0,
                num_pit_stops=0,
                fuel_percent=0,
                player_name="Driver One",
                track="SO1",
                car="UF1",
            ),
        ),
        ("state", StateEvent(flags2=0, track="BL2", car="UF1")),
        (
            "lap",
            LapEvent(
                plid=6,
                lap_time_ms=64000,
                estimate_time_ms=0,
                flags=0,
                penalty=0,
                num_pit_stops=0,
                fuel_percent=0,
                player_name="Driver Two",
                track="BL2",
                car="UF1",
            ),
        ),
    ]

    base_frame_kwargs = dict(
        ang_vel=(0.0, 0.0, 0.0),
        heading=(0.0, 1.0, 0.0),
        acceleration=(0.0, 0.0, 0.0),
        velocity=(0.0, 0.0, 0.0),
        position=(0.0, 0.0, 0.0),
    )
    FakeOutSimClient.frames_to_yield = [
        OutSimFrame(time_ms=idx * 1000, **base_frame_kwargs)
        for idx in range(1, len(FakeInSimClient.events) + 1)
    ]

    try:
        main_module.main()
    finally:
        FakeInSimClient.events = []
        FakeOutSimClient.frames_to_yield = []

    assert record_calls == [("BL2", "UF1", 64000)]
