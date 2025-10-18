from __future__ import annotations

from main import clear_session_timing, update_session_best


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
