# Varshini does B content


import math
import random
import pytest

from src.detectorB import PING, FOUND

from src.improvedB import (
    getDistanceMapB,
    getExpectedInformationGainB,
    chooseImprovedTargetB,
    getImprovedMoveB,
    improvedBStep
)


def testDistanceMapOpenGridB():
    # shortest path distances should be straightforward when
    # there are no walls getting in the way
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    distanceMap = getDistanceMapB(grid, (0, 0))

    assert distanceMap[(0, 0)] == 0
    assert distanceMap[(0, 1)] == 1
    assert distanceMap[(2, 2)] == 4


def testDistanceMapAvoidsWallsB():
    # blocked cells cannot appear as reachable positions
    # and the distance needs to reflect the detour around the wall
    grid = [
        [1, 0, 1],
        [1, 1, 1]
    ]

    distanceMap = getDistanceMapB(grid, (0, 0))

    assert (0, 1) not in distanceMap
    assert distanceMap[(0, 2)] == 4


def testInformationGainNonnegativeB():
    # information gain should never be negative
    # an observation cannot increase expected uncertainty on average
    knowledgeBase = {
        (0, 1): 0.3,
        (0, 3): 0.4,
        (0, 5): 0.3
    }

    informationGain = getExpectedInformationGainB(
        knowledgeBase, (0, 0), 0.5
    )

    assert informationGain >= 0


def testInformationGainZeroForCertainLocationB():
    # when the location is already known with probability 1
    # there is no uncertainty left for a detector reading to remove
    knowledgeBase = {
        (0, 2): 1.0
    }

    informationGain = getExpectedInformationGainB(
        knowledgeBase, (0, 0), 0.5
    )

    assert informationGain == pytest.approx(0.0)


def testInformationGainPositiveForUncertainLocationB():
    # two possible locations with different ping likelihoods
    # should produce a detector reading that teaches us something
    knowledgeBase = {
        (0, 1): 0.5,
        (0, 4): 0.5
    }

    informationGain = getExpectedInformationGainB(
        knowledgeBase, (0, 0), 0.5
    )

    assert informationGain > 0


def testInformationGainBoundedByPriorEntropyB():
    # a detector cannot reveal more information about the lost bot
    # than the uncertainty that existed in the first place
    knowledgeBase = {
        (0, 1): 0.25,
        (0, 2): 0.25,
        (0, 3): 0.25,
        (0, 4): 0.25
    }

    priorEntropy = -sum(
        probability * math.log2(probability)
        for probability in knowledgeBase.values()
    )

    informationGain = getExpectedInformationGainB(
        knowledgeBase, (0, 0), 0.5
    )

    assert informationGain <= priorEntropy + 1e-10


def testImprovedTargetReachableB():
    # whatever target the heuristic selects, it must be
    # an actual reachable cell on the ship
    grid = [
        [1, 0, 1],
        [1, 1, 1]
    ]

    knowledgeBase = {
        (0, 0): 0.1,
        (0, 2): 0.9
    }

    targetPosition = chooseImprovedTargetB(
        grid,
        (0, 0),
        knowledgeBase,
        0.4,
        rng=random.Random(10)
    )

    distanceMap = getDistanceMapB(grid, (0, 0))

    assert targetPosition in distanceMap


def testImprovedMoveLegalB():
    # the chosen next position must either be the current cell
    # or a neighboring open cell, no jumping across the grid
    grid = [
        [1, 0, 1],
        [1, 1, 1]
    ]

    knowledgeBase = {
        (0, 2): 1.0
    }

    nextPosition = getImprovedMoveB(
        grid,
        (0, 0),
        knowledgeBase,
        0.5,
        rng=random.Random(3)
    )

    assert nextPosition in {(0, 0), (1, 0)}


def testFreeMovementTargetReachableB():
    # Question 6 makes movement free, but that doesn't mean
    # we can select blocked cells as detector locations
    grid = [
        [1, 0, 1],
        [1, 1, 1]
    ]

    knowledgeBase = {
        (0, 0): 0.1,
        (0, 2): 0.9
    }

    targetPosition = chooseImprovedTargetB(
        grid,
        (0, 0),
        knowledgeBase,
        0.5,
        movementCost=0.0,
        rng=random.Random(4)
    )

    distanceMap = getDistanceMapB(grid, (0, 0))

    assert targetPosition in distanceMap


def testImprovedTargetSeedReproducibilityB():
    # same inputs and same random seed should make the heuristic
    # choose the same target, which helps reproduce our experiments
    grid = [
        [1, 1],
        [1, 1]
    ]

    knowledgeBase = {
        (0, 1): 0.5,
        (1, 0): 0.5
    }

    firstTarget = chooseImprovedTargetB(
        grid,
        (0, 0),
        knowledgeBase,
        0.5,
        rng=random.Random(20)
    )

    secondTarget = chooseImprovedTargetB(
        grid,
        (0, 0),
        knowledgeBase,
        0.5,
        rng=random.Random(20)
    )

    assert firstTarget == secondTarget


def testImprovedStepUpdatesBeliefsB():
    # the improved strategy still needs to update its posterior
    # correctly before it decides where to go next
    grid = [[1, 1, 1, 1]]

    knowledgeBase = {
        (0, 1): 0.5,
        (0, 3): 0.5
    }

    nextPosition, updatedBeliefs = improvedBStep(
        grid,
        (0, 0),
        knowledgeBase,
        PING,
        0.5,
        rng=random.Random(5)
    )

    assert updatedBeliefs[(0, 1)] > updatedBeliefs[(0, 3)]
    assert sum(updatedBeliefs.values()) == pytest.approx(1.0)
    assert nextPosition in {(0, 0), (0, 1)}


def testImprovedFoundB():
    # once FOUND happens, the search is over
    # no additional moves should be requested
    grid = [[1, 1]]

    knowledgeBase = {
        (0, 0): 1.0
    }

    nextPosition, updatedBeliefs = improvedBStep(
        grid,
        (0, 0),
        knowledgeBase,
        FOUND,
        0.5
    )

    assert nextPosition == (0, 0)
    assert updatedBeliefs[(0, 0)] == pytest.approx(1.0)


def testInvalidMovementCostB():
    # negative movement cost makes no physical sense
    # and would completely mess up our scoring heuristic
    grid = [[1, 1]]

    knowledgeBase = {
        (0, 1): 1.0
    }

    with pytest.raises(ValueError):
        chooseImprovedTargetB(
            grid,
            (0, 0),
            knowledgeBase,
            0.5,
            movementCost=-1.0
        )


def testInvalidDetectorCostB():
    # detector cost must be positive because the heuristic
    # divides by total action cost when evaluating targets
    grid = [[1, 1]]

    knowledgeBase = {
        (0, 1): 1.0
    }

    with pytest.raises(ValueError):
        chooseImprovedTargetB(
            grid,
            (0, 0),
            knowledgeBase,
            0.5,
            detectorCost=0.0
        )
