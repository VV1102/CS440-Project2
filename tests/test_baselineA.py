from src.baselineA import runBaselineA


def test_same_start():
    grid = [
        [1, 1],
        [1, 1]
    ]

    result = runBaselineA(grid, (0, 0), (0, 0), 1)

    assert result["found"] is True
    assert result["moves"] == 0
    assert result["detector_actions"] == 1
    assert result["total_cost"] == 0.5


def test_adjacent_bot():
    grid = [
        [1, 1],
        [1, 1]
    ]

    result = runBaselineA(grid, (0, 0), (0, 1), 1)

    assert result["found"] is True
    assert result["total_cost"] == (
        result["moves"] + 0.5 * result["detector_actions"]
    )


def test_far_bot():
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    result = runBaselineA(grid, (0, 0), (2, 2), 1)

    assert result["found"] is True
    assert result["moves"] >= 1


def test_zero_radius():
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    result = runBaselineA(grid, (0, 0), (2, 2), 0)

    assert result["found"] is True
