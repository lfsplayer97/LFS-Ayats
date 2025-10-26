"""Telemetry persistence helpers for storing personal best lap times."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Optional, Set, Tuple

__all__ = [
    "PersonalBestRecord",
    "load_personal_best",
    "record_lap",
    "delete_personal_best",
]

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DEFAULT_DB_PATH = _DATA_DIR / "telemetry.db"
_MIGRATIONS_DIR = _DATA_DIR / "migrations"


@dataclass(frozen=True)
class PersonalBestRecord:
    """Represents a stored personal best entry for a track and car."""

    track: str
    car: str
    laptime_ms: int
    recorded_at: datetime


def _load_migration_versions() -> Iterable[Path]:
    if not _MIGRATIONS_DIR.exists():
        return []
    return sorted(_MIGRATIONS_DIR.glob("*.sql"))


def _apply_migrations(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY
        )
        """
    )

    cur = conn.execute("SELECT version FROM schema_migrations")
    applied: Set[str] = {row[0] for row in cur.fetchall()}

    for migration_path in _load_migration_versions():
        version = migration_path.stem
        if version in applied:
            continue

        sql = migration_path.read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO schema_migrations(version) VALUES (?)",
            (version,),
        )
        conn.commit()


def _initialise(conn: sqlite3.Connection) -> None:
    _apply_migrations(conn)


@contextmanager
def _connect(db_path: Optional[Path] = None) -> Iterator[sqlite3.Connection]:
    path = Path(db_path) if db_path is not None else _DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    try:
        conn.row_factory = sqlite3.Row
        _initialise(conn)
        yield conn
    finally:
        conn.close()


def _parse_row(row: sqlite3.Row) -> PersonalBestRecord:
    timestamp = datetime.fromisoformat(row["date"])
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    else:
        timestamp = timestamp.astimezone(timezone.utc)
    return PersonalBestRecord(
        track=row["track"],
        car=row["car"],
        laptime_ms=int(row["laptime_ms"]),
        recorded_at=timestamp,
    )


def load_personal_best(
    track: str, car: str, *, db_path: Optional[Path] = None
) -> Optional[PersonalBestRecord]:
    """Return the stored PB for the given track/car combination if it exists."""

    with _connect(db_path) as conn:
        cur = conn.execute(
            "SELECT track, car, laptime_ms, date FROM pb WHERE track = ? AND car = ?",
            (track, car),
        )
        row = cur.fetchone()
    if row is None:
        return None
    return _parse_row(row)


def record_lap(
    track: str,
    car: str,
    laptime_ms: int,
    *,
    timestamp: Optional[datetime] = None,
    db_path: Optional[Path] = None,
) -> Tuple[PersonalBestRecord, bool]:
    """Persist a lap time and return the active PB along with an improvement flag."""

    if laptime_ms < 0:
        raise ValueError("Lap time must be non-negative")

    timestamp = timestamp or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    else:
        timestamp = timestamp.astimezone(timezone.utc)
    iso_timestamp = timestamp.isoformat()

    with _connect(db_path) as conn:
        cur = conn.execute(
            "SELECT track, car, laptime_ms, date FROM pb WHERE track = ? AND car = ?",
            (track, car),
        )
        existing = cur.fetchone()

        if existing is None or laptime_ms < int(existing["laptime_ms"]):
            conn.execute(
                """
                INSERT INTO pb(track, car, laptime_ms, date)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(track, car) DO UPDATE SET
                    laptime_ms = excluded.laptime_ms,
                    date = excluded.date
                """,
                (track, car, int(laptime_ms), iso_timestamp),
            )
            conn.commit()
            return (
                PersonalBestRecord(
                    track=track, car=car, laptime_ms=int(laptime_ms), recorded_at=timestamp
                ),
                True,
            )

        return _parse_row(existing), False


def delete_personal_best(
    track: str, car: str, *, db_path: Optional[Path] = None
) -> bool:
    """Delete a stored PB and return ``True`` if a record was removed."""

    with _connect(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM pb WHERE track = ? AND car = ?",
            (track, car),
        )
        conn.commit()
        return cur.rowcount > 0
