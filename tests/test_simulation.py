# Varshini & Sri will write together once all dependent parts are done


# Sri does simulation tests

# Tests for complete LocatorBot simulations.

#These tests check whether the simulator correctly connects detection,
# knowledge-base updates, movement decisions, and the discovery cost.
# We also test edge cases so the search doesn't secretly break on tiny grids.


import math
import random

import pytest

from src.simulation import (
    calculateDiscoveryCost,
    validateSimulationInputs,
    chooseNearestPossibleCell,
    chooseImprovedTargetA,
    chooseSimulationTarget,
    getSimulationPath,
    runSimulation,
    runAllStrategies
)


def testCalculateDiscoveryCostNormal():
    # the professor's normal cost formula is moves + 0.5 * detector actions
    # so 7 moves and 4 detector actions should cost 9 total
    totalCost = calculateDiscoveryCost(7, 4)

    assert totalCost == 9.0


def testCalculateDiscoveryCostFreeMovement():
    # Q6 changes the movement cost to zero, so even if the bot walks
    # around a lot, only its detector actions contribute to discovery cost
    totalCost = calculateDiscoveryCost(
        moveCount=100,
        detectorCount=8,
        movementCost=0,
        detectorCost=1
    )

    assert totalCost == 8.0


def testCalculateDiscoveryCostRejectsInvalidValues():
    # negative costs and action counts don't make physical sense
    # can't have the bot taking -3 steps bro what
    with pytest.raises(ValueError):
        calculateDiscoveryCost(-3, 5)

    with pytest.raises(ValueError):
        calculateDiscoveryCost(3, -5)

    with pytest.raises(ValueError):
        calculateDiscoveryCost(3, 5, movementCost=-1)

    with pytest.raises(ValueError):
        calculateDiscoveryCost(3, 5, detectorCost=0)


def testValidateSimulationInputsAcceptsValidGrid():
    # a simple open corridor is enough for a valid simulation
    # the two bots are on reachable open cells and both detector
    # parameters satisfy the assignment's constraints
    grid = [[1, 1, 1]]

    validateSimulationInputs(
        grid, (0, 0), (0, 2),
        "B", "baseline", None, 0.5,
        1.0, 0.5, 100
    )


@pytest.mark.parametrize(
    "detectorType,strategy,k,alpha",
    [
        ("C", "baseline", None, 0.5),
        ("A", "random", 1, None),
        ("A", "baseline", -1, None),
        ("A", "baseline", 1.5, None),
        ("B", "baseline", None, 0),
        ("B", "improved", None, -0.5),
        ("B", "improved", None, math.inf)
    ]
)
def testValidateSimulationInputsRejectsBadParameters(
        detectorType, strategy, k, alpha):
    # every detector has its own valid parameter range
    # Type A needs a nonnegative integer k, Type B needs alpha > 0
    # invalid configurations should fail before the trial begins
    grid = [[1, 1]]

    with pytest.raises(ValueError):
        validateSimulationInputs(
            grid, (0, 0), (0, 1),
            detectorType, strategy, k, alpha,
            1.0, 0.5, 100
        )


def testValidateSimulationInputsRejectsBlockedPosition():
    # LocatorBot and LostBot must both occupy open cells
    # walls are not legal starting positions, obviously
    grid = [
        [1, 0],
        [1, 1]
    ]

    with pytest.raises(ValueError):
        runSimulation(
            grid, (0, 1), (1, 1),
            detectorType="A", strategy="baseline", k=1
        )


def testValidateSimulationInputsRejectsDisconnectedGrid():
    # even if both positions are open, the search is impossible
    # when there is no walkable path between the two bots
    grid = [[1, 0, 1]]

    with pytest.raises(ValueError):
        runSimulation(
            grid, (0, 0), (0, 2),
            detectorType="A", strategy="baseline", k=1
        )


def testChooseNearestPossibleCellUsesBfsDistance():
    # the nearest candidate should be based on the actual walkable
    # path rather than Euclidean distance through blocked cells
    grid = [
        [1, 0, 1],
        [1, 1, 1]
    ]

    possibleCells = {(1, 0), (0, 2)}

    targetPosition = chooseNearestPossibleCell(
        grid, (0, 0), possibleCells, random.Random(10)
    )

    assert targetPosition == (1, 0)


def testChooseNearestPossibleCellRejectsEmptyCandidates():
    # if there are no possible locations, the search cannot
    # choose a meaningful target and should report the issue
    grid = [[1, 1]]

    with pytest.raises(RuntimeError):
        chooseNearestPossibleCell(grid, (0, 0), set())


def testGetSimulationPathAvoidsWalls():
    # this is the same wall-navigation case that caught our earlier
    # rectangular-grid bug in ship.py, so we're keeping it here too
    # bfs must route around the wall instead of cutting through it
    grid = [
        [1, 0, 1],
        [1, 1, 1]
    ]

    path = getSimulationPath(grid, (0, 0), (0, 2))

    assert path == [
        (0, 0),
        (1, 0),
        (1, 1),
        (1, 2),
        (0, 2)
    ]


def testGetSimulationPathRejectsUnreachableTarget():
    # a target behind an impassable wall cannot be reached
    # so the simulator should fail rather than pretending it moved there
    grid = [[1, 0, 1]]

    with pytest.raises(RuntimeError):
        getSimulationPath(grid, (0, 0), (0, 2))


@pytest.mark.parametrize(
    "detectorType,strategy",
    [
        ("A", "baseline"),
        ("A", "improved"),
        ("B", "baseline"),
        ("B", "improved")
    ]
)
def testAllStrategiesFindLostBotOnSmallShip(detectorType, strategy):
    # run each of the four strategies on the same tiny ship
    # every strategy should eventually reach the stationary LostBot
    # and the final position should match the hidden location
    grid = [[1, 1, 1]]

    result = runSimulation(
        grid=grid,
        locatorPosition=(0, 0),
        lostBotPosition=(0, 2),
        detectorType=detectorType,
        strategy=strategy,
        k=1,
        alpha=0.5,
        maxActions=200,
        rng=random.Random(15)
    )

    assert result["found"] is True
    assert result["final_position"] == (0, 2)
    assert result["detector_actions"] >= 1
    assert result["moves"] >= 2


@pytest.mark.parametrize(
    "detectorType,strategy",
    [
        ("A", "baseline"),
        ("A", "improved"),
        ("B", "baseline"),
        ("B", "improved")
    ]
)
def testSameStartingPositionFoundImmediately(detectorType, strategy):
    # if the bots start on the same cell, the very first detector
    # action should return FOUND and no movement should be necessary
    grid = [[1, 1]]

    result = runSimulation(
        grid=grid,
        locatorPosition=(0, 0),
        lostBotPosition=(0, 0),
        detectorType=detectorType,
        strategy=strategy,
        k=1,
        alpha=0.5,
        rng=random.Random(2)
    )

    assert result["found"] is True
    assert result["moves"] == 0
    assert result["detector_actions"] == 1
    assert result["total_cost"] == 0.5
    assert result["position_history"] == [(0, 0)]


def testBaselineAFindsLostBotWithNoPing():
    # with k=0, Type A can only ping when both bots share a cell
    # since same-cell detection is FOUND, the bot must search by
    # eliminating positions and moving toward remaining candidates
    grid = [[1, 1, 1]]

    result = runSimulation(
        grid, (0, 0), (0, 2),
        detectorType="A",
        strategy="baseline",
        k=0,
        rng=random.Random(4)
    )

    assert result["found"] is True
    assert result["final_position"] == (0, 2)
    assert result["detector_history"][-1] == "found"


def testTypeBUsesUppercaseDetectorResults():
    # our Type B detector returns uppercase PING, NO_PING and FOUND
    # while our partner's Type A detector uses lowercase strings
    # the simulator needs to handle both without mixing them up
    grid = [[1, 1]]

    result = runSimulation(
        grid, (0, 0), (0, 1),
        detectorType="B",
        strategy="baseline",
        alpha=0.5,
        rng=random.Random(5)
    )

    assert result["detector_history"][-1] == "FOUND"
    assert all(
        detectorResult in ("PING", "NO_PING", "FOUND")
        for detectorResult in result["detector_history"]
    )


def testEveryNormalMoveIsAdjacent():
    # during normal-cost trials, the bot moves one cell at a time
    # consecutive positions must differ by exactly one row or column
    # no diagonals and definitely no teleportation through walls
    grid = [
        [1, 0, 1],
        [1, 1, 1]
    ]

    result = runSimulation(
        grid, (0, 0), (0, 2),
        detectorType="B",
        strategy="baseline",
        alpha=0.5,
        rng=random.Random(3)
    )

    positionHistory = result["position_history"]

    for firstPosition, secondPosition in zip(
            positionHistory, positionHistory[1:]
    ):
        rowDifference = abs(firstPosition[0] - secondPosition[0])
        colDifference = abs(firstPosition[1] - secondPosition[1])

        assert rowDifference + colDifference == 1
        assert grid[secondPosition[0]][secondPosition[1]] == 1


def testNormalCostMatchesRecordedActions():
    # we independently recalculate the cost using the returned counts
    # this catches cases where the simulator accidentally forgets to
    # charge for a detector action or counts a move twice
    grid = [[1, 1, 1]]

    result = runSimulation(
        grid, (0, 0), (0, 2),
        detectorType="A",
        strategy="baseline",
        k=1,
        rng=random.Random(8)
    )

    expectedCost = result["moves"] + 0.5 * result["detector_actions"]

    assert result["total_cost"] == expectedCost
    assert result["moves"] == len(result["position_history"]) - 1
    assert result["detector_actions"] == len(result["detector_history"])


@pytest.mark.parametrize(
    "detectorType,strategy",
    [
        ("A", "baseline"),
        ("A", "improved"),
        ("B", "baseline"),
        ("B", "improved")
    ]
)
def testFreeMovementCountsOnlyDetectorActions(detectorType, strategy):
    # Question 6 makes movement free but detector actions still cost
    # so we should get the detector count as the total cost when
    # detectorCost=1 and movementCost=0
    grid = [[1, 1, 1, 1]]

    result = runSimulation(
        grid, (0, 0), (0, 3),
        detectorType=detectorType,
        strategy=strategy,
        k=1,
        alpha=0.5,
        movementCost=0,
        detectorCost=1,
        maxActions=200,
        rng=random.Random(11)
    )

    assert result["found"] is True
    assert result["total_cost"] == result["detector_actions"]
    assert result["movement_cost"] == 0
    assert result["final_position"] == (0, 3)


def testFreeMovementCanTravelEntirePathBeforeScanning(monkeypatch):
    # this isolates the Q6 movement rule by forcing a target several
    # cells away. we want the bot to travel there before detecting again
    # instead of scanning at every intermediate cell
    grid = [[1, 1, 1, 1]]

    def fixedTarget(*args, **kwargs):
        return (0, 3)

    monkeypatch.setattr(
        "src.simulation.chooseSimulationTarget",
        fixedTarget
    )

    result = runSimulation(
        grid, (0, 0), (0, 3),
        detectorType="A",
        strategy="baseline",
        k=0,
        movementCost=0,
        detectorCost=1
    )

    assert result["moves"] == 3
    assert result["detector_actions"] == 2
    assert result["total_cost"] == 2
    assert result["position_history"] == [
        (0, 0), (0, 1), (0, 2), (0, 3)
    ]


def testSimulationStopsAtActionLimit():
    # a broken or unlucky strategy should not be able to loop forever
    # maxActions is a safety limit, not a fake successful discovery
    grid = [[1, 1, 1]]

    with pytest.raises(RuntimeError, match="maximum number of actions"):
        runSimulation(
            grid, (0, 0), (0, 2),
            detectorType="A",
            strategy="baseline",
            k=0,
            maxActions=1
        )


def testSimulationDoesNotChangeOriginalGrid():
    # the LostBot is stationary and the ship itself should not change
    # searching doesn't mean we get to open walls or modify the maze
    grid = [
        [1, 0, 1],
        [1, 1, 1]
    ]

    originalGrid = [gridRow[:] for gridRow in grid]

    runSimulation(
        grid, (0, 0), (0, 2),
        detectorType="A",
        strategy="baseline",
        k=1,
        rng=random.Random(12)
    )

    assert grid == originalGrid


def testSeededTypeBTrialIsReproducible():
    # Type B uses random detector outcomes, so using the same seed
    # should produce the same observations and movement decisions
    # this helps us debug experiments without chasing random ghosts
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    firstResult = runSimulation(
        grid, (0, 0), (2, 2),
        detectorType="B",
        strategy="baseline",
        alpha=0.5,
        rng=random.Random(42)
    )

    secondResult = runSimulation(
        grid, (0, 0), (2, 2),
        detectorType="B",
        strategy="baseline",
        alpha=0.5,
        rng=random.Random(42)
    )

    assert firstResult == secondResult


def testRunAllStrategiesReturnsFourResults():
    # experiments.py needs all four strategies to have consistent
    # output fields so it can compare costs without special cases
    grid = [[1, 1, 1]]

    allResults = runAllStrategies(
        grid=grid,
        locatorPosition=(0, 0),
        lostBotPosition=(0, 2),
        k=1,
        alpha=0.5,
        seed=25
    )

    assert set(allResults) == {
        "A_baseline",
        "A_improved",
        "B_baseline",
        "B_improved"
    }

    for result in allResults.values():
        assert result["found"] is True
        assert result["final_position"] == (0, 2)
        assert "moves" in result
        assert "detector_actions" in result
        assert "total_cost" in result


def testRunAllStrategiesWithFreeMovement():
    # Q6 needs the same four strategies compared when movement is free
    # this checks the experiment helper passes the new cost rules to all
    grid = [[1, 1, 1]]

    allResults = runAllStrategies(
        grid=grid,
        locatorPosition=(0, 0),
        lostBotPosition=(0, 2),
        k=1,
        alpha=0.5,
        movementCost=0,
        detectorCost=1,
        seed=30
    )

    for result in allResults.values():
        assert result["found"] is True
        assert result["total_cost"] == result["detector_actions"]
