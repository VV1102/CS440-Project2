import pytest
from src.pathfinding import bfs
from src.improvedA import calculateInformationGain
from src.improvedA import chooseBestScanPosition
from src.improvedA import runImprovedA 

def test_balanced_scan():
    possibleCells = {
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3)
    }

    result = calculateInformationGain(
        possibleCells,
        (0, 0),
        1
    )

    # Two cells inside, two outside
    # Maximum binary entropy = 1
    assert result == pytest.approx(1.0)


def test_no_information():
    possibleCells = {
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1)
    }

    result = calculateInformationGain(
        possibleCells,
        (0, 0),
        2
    )

    # All candidates are inside the detector range
    assert result == 0

def test_choose_valid_position():
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    possibleCells = {
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1), (1, 2),
        (2, 0), (2, 1), (2, 2)
    }

    result = chooseBestScanPosition(
        grid, (0, 0), possibleCells, 1
    )

    assert result in possibleCells


def test_choose_reachable_position():
    grid = [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 1]
    ]

    possibleCells = {
        (0, 0), (0, 1),
        (1, 1), (1, 2), (2, 2)
    }

    result = chooseBestScanPosition(
        grid, (0, 0), possibleCells, 1
    )

    assert result is not None
    assert bfs(grid, (0, 0), result) is not None

def test_improved_same_start():
    grid = [
        [1, 1],
        [1, 1]
    ]

    result = runImprovedA(grid, (0, 0), (0, 0), 1)

    assert result["found"] is True
    assert result["moves"] == 0
    assert result["detector_actions"] == 1


def test_improved_far_bot():
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    result = runImprovedA(grid, (0, 0), (2, 2), 1)

    assert result["found"] is True
    assert result["total_cost"] == (
        result["moves"] + 0.5 * result["detector_actions"]
    )


def test_improved_zero_radius():
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    result = runImprovedA(grid, (0, 0), (2, 2), 0)

    assert result["found"] is True
