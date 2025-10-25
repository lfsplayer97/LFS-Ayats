import math

import pytest

from src.radar import compute_radar_targets


def _normalise(angle: float) -> float:
    wrapped = (angle + math.pi) % (2 * math.pi)
    return wrapped - math.pi


def extract_distances(targets):
    return [target.distance for target in targets]


def test_compute_radar_targets_filters_and_sorts() -> None:
    player = (0.0, 0.0)
    heading = 0.0
    others = [
        (0.0, 10.0),
        (50.0, 0.0),
        (-1.0, -1.0),
        (0.0, 500.0),
    ]

    targets = compute_radar_targets(player, heading, others, max_range=140.0)

    assert extract_distances(targets) == sorted(extract_distances(targets))
    assert len(targets) == 3
    assert math.isclose(targets[0].distance, math.sqrt(2), rel_tol=1e-9)
    assert math.isclose(targets[-1].distance, 50.0)


def test_compute_radar_targets_returns_expected_bearings() -> None:
    player = (10.0, -20.0)
    heading = math.radians(30.0)
    others = [
        (10.0, -10.0),
        (20.0, -20.0),
        (0.0, -25.0),
    ]

    targets = compute_radar_targets(player, heading, others, max_range=200.0)

    bearings = [target.bearing for target in targets]

    expected = []
    for other in others:
        offset_x = other[0] - player[0]
        offset_y = other[1] - player[1]
        world_angle = math.atan2(offset_x, offset_y)
        expected.append(_normalise(world_angle - heading))

    assert bearings[0] == pytest.approx(expected[0], abs=1e-6)
    assert bearings[1] == pytest.approx(expected[1], abs=1e-6)
    assert bearings[2] == pytest.approx(expected[2], abs=1e-6)


def test_compute_radar_targets_normalises_extreme_bearings() -> None:
    player = (0.0, 0.0)
    heading = -math.pi + 0.1
    others = [(0.0, -10.0)]

    targets = compute_radar_targets(player, heading, others, max_range=500.0)
    assert len(targets) == 1
    bearing = targets[0].bearing
    assert -math.pi <= bearing <= math.pi
    assert bearing == pytest.approx(-0.1, abs=1e-6)


def test_compute_radar_targets_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        compute_radar_targets((0.0,), 0.0, [])

    with pytest.raises(ValueError):
        compute_radar_targets((0.0, float("nan")), 0.0, [])

    with pytest.raises(ValueError):
        compute_radar_targets((0.0, 0.0), 0.0, [], max_range=0.0)

    targets = compute_radar_targets((0.0, 0.0), 0.0, [(float("nan"), 1.0)])
    assert targets == []
