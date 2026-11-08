# Varshini does B content


import random
import pytest

from src.detectorB import PING, NO_PING, FOUND

from src.baselineB import (
    chooseBaselineTargetB,
    getBaselineMoveB,
    baselineBStep
)


def testHighestProbabilityTargetB():
    # baseline should choose the location with the greatest posterior
    # probability, even if another possible location is closer
    grid = [
        [1, 1, 1],
        [1, 1, 1]
    ]

    knowledgeBase = {
        (0, 2): 0.8,
        (1, 0): 0.2
    }

    targetPosition = chooseBaselineTargetB(
        grid, (0, 0), knowledgeBase
    )

    assert targetPosition == (0, 2)


def testTieBrokenByShortestPathB():
    # if two locations are equally likely, prefer the one that
    # requires fewer actual moves through the ship
    grid = [
        [1, 1, 1],
        [1, 1, 1]
    ]

    knowledgeBase = {
        (0, 2): 0.5,
        (1, 0): 0.5
    }

    targetPosition = chooseBaselineTargetB(
        grid, (0, 0), knowledgeBase
    )

    assert targetPosition == (1, 0)


def testRandomTieReproducibilityB():
    # equal probability AND equal walking distance means random tie
    # using the same seed should give the same chosen target
    grid = [
        [1, 1],
        [1, 1]
    ]

    knowledgeBase = {
        (0, 1): 0.5,
        (1, 0): 0.5
    }

    firstTarget = chooseBaselineTargetB(
        grid,
        (0, 0),
        knowledgeBase,
        random.Random(15)
    )

    secondTarget = chooseBaselineTargetB(
        grid,
        (0, 0),
        knowledgeBase,
        random.Random(15)
    )

    assert firstTarget == secondTarget
    assert firstTarget in {(0, 1), (1, 0)}


def testBaselineMovesOneCellB():
    # selecting a distant target does not mean teleporting there
    # movement is still one adjacent open cell at a time
    grid = [[1, 1, 1, 1]]

    knowledgeBase = {
        (0, 3): 1.0
    }

    nextPosition = getBaselineMoveB(
        grid, (0, 0), knowledgeBase
    )

    assert nextPosition == (0, 1)


def testBaselineAvoidsBlockedCellsB():
    # direct route is blocked, so BFS needs to go around the wall
    grid = [
        [1, 0, 1],
        [1, 1, 1]
    ]

    knowledgeBase = {
        (0, 2): 1.0
    }

    nextPosition = getBaselineMoveB(
        grid, (0, 0), knowledgeBase
    )

    assert nextPosition == (1, 0)


def testBaselineUpdatesBeforeMovingB():
    # after a ping, the nearby candidate should become more likely
    # and the bot should move toward the updated best location
    grid = [[1, 1, 1, 1]]

    knowledgeBase = {
        (0, 1): 0.5,
        (0, 3): 0.5
    }

    nextPosition, updatedBeliefs = baselineBStep(
        grid,
        (0, 0),
        knowledgeBase,
        PING,
        0.5
    )

    assert updatedBeliefs[(0, 1)] > updatedBeliefs[(0, 3)]
    assert nextPosition == (0, 1)


def testNoPingChangesBaselineTargetB():
    # no ping rules out the adjacent candidate completely
    # so the bot should redirect toward the remaining possibility
    grid = [[1, 1, 1, 1]]

    knowledgeBase = {
        (0, 1): 0.5,
        (0, 3): 0.5
    }

    nextPosition, updatedBeliefs = baselineBStep(
        grid,
        (0, 0),
        knowledgeBase,
        NO_PING,
        0.5
    )

    assert updatedBeliefs[(0, 1)] == 0
    assert updatedBeliefs[(0, 3)] == pytest.approx(1.0)
    assert nextPosition == (0, 1)


def testBaselineFoundStopsMovementB():
    # if the bot is found, we shouldn't keep planning more moves
    grid = [[1, 1]]

    knowledgeBase = {
        (0, 0): 1.0
    }

    nextPosition, updatedBeliefs = baselineBStep(
        grid,
        (0, 0),
        knowledgeBase,
        FOUND,
        0.5
    )

    assert nextPosition == (0, 0)
    assert updatedBeliefs[(0, 0)] == pytest.approx(1.0)


def testBaselineRejectsImpossibleTargetB():
    # cannot choose a target when every candidate has zero probability
    # this is an invalid belief state, not a normal navigation problem
    grid = [[1, 1]]

    knowledgeBase = {
        (0, 1): 0.0
    }

    with pytest.raises(ValueError):
        chooseBaselineTargetB(
            grid, (0, 0), knowledgeBase
        )
