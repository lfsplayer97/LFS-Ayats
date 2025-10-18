from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.persistence import PersonalBestRecord, load_personal_best, record_lap


def test_load_returns_none_when_missing(tmp_path: Path) -> None:
    db_path = tmp_path / "telemetry.db"
    assert load_personal_best("BL1", "XFG", db_path=db_path) is None


def test_record_lap_creates_and_updates_pb(tmp_path: Path) -> None:
    db_path = tmp_path / "telemetry.db"

    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    record, improved = record_lap("BL1", "XFG", 75000, timestamp=timestamp, db_path=db_path)
    assert improved is True
    assert isinstance(record, PersonalBestRecord)
    assert record.track == "BL1"
    assert record.car == "XFG"
    assert record.laptime_ms == 75000
    assert record.recorded_at == timestamp

    # Slower lap should not replace PB
    slower_record, slower_improved = record_lap(
        "BL1", "XFG", 76000, timestamp=timestamp.replace(day=2), db_path=db_path
    )
    assert slower_improved is False
    assert slower_record.laptime_ms == 75000
    assert slower_record.recorded_at == timestamp

    # Faster lap updates PB and timestamp
    faster_timestamp = datetime(2024, 1, 3, tzinfo=timezone.utc)
    faster_record, faster_improved = record_lap(
        "BL1", "XFG", 74000, timestamp=faster_timestamp, db_path=db_path
    )
    assert faster_improved is True
    assert faster_record.laptime_ms == 74000
    assert faster_record.recorded_at == faster_timestamp

    loaded = load_personal_best("BL1", "XFG", db_path=db_path)
    assert loaded == faster_record
