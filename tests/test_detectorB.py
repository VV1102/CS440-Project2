# Varshini does B content


import math
import random
import pytest

from src.detectorB import (
    PING,
    NO_PING,
    FOUND,
    getEuclideanDistance,
    getPingProbability,
    runDetectorB
)


def testEuclideanDistanceB():
    # using the good old 3-4-5 triangle here because if this
    # somehow fails then our entire distance calculation is cooked
    firstPosition = (0, 0)
    secondPosition = (3, 4)

    distance = getEuclideanDistance(firstPosition, secondPosition)

    assert distance == pytest.approx(5.0)


def testDistanceIsSymmetricB():
    # switching the order of two positions should not change
    # the distance between them. basic geometry but we test it anyway
    firstPosition = (2, 7)
    secondPosition = (9, 3)

    firstDistance = getEuclideanDistance(firstPosition, secondPosition)
    secondDistance = getEuclideanDistance(secondPosition, firstPosition)

    assert firstDistance == pytest.approx(secondDistance)


def testAdjacentCellAlwaysPingsB():
    # euclidean distance of 1 makes the exponent zero
    # meaning the ping probability is exactly 1, regardless of alpha
    locatorPosition = (2, 2)
    lostBotPosition = (2, 3)

    for alpha in (0.1, 0.5, 1.0, 3.0):
        pingProbability = getPingProbability(
            locatorPosition, lostBotPosition, alpha
        )

        assert pingProbability == pytest.approx(1.0)
        assert runDetectorB(
            locatorPosition, lostBotPosition, alpha
        ) == PING


def testPingProbabilityFormulaB():
    # manually calculating the expected probability to make sure
    # the function follows the actual formula, not some BFS distance
    locatorPosition = (0, 0)
    lostBotPosition = (3, 4)
    alpha = 0.5

    expectedProbability = math.exp(-alpha * (5 - 1))

    actualProbability = getPingProbability(
        locatorPosition, lostBotPosition, alpha
    )

    assert actualProbability == pytest.approx(expectedProbability)


def testProbabilityDecreasesWithDistanceB():
    # further away = weaker signal, as it should be
    locatorPosition = (0, 0)
    alpha = 0.6

    nearbyProbability = getPingProbability(
        locatorPosition, (0, 2), alpha
    )
    distantProbability = getPingProbability(
        locatorPosition, (0, 7), alpha
    )

    assert nearbyProbability > distantProbability


def testProbabilityDecreasesWithAlphaB():
    # higher alpha means signal strength drops faster
    # for distances greater than 1
    locatorPosition = (0, 0)
    lostBotPosition = (0, 5)

    lowAlphaProbability = getPingProbability(
        locatorPosition, lostBotPosition, 0.2
    )
    highAlphaProbability = getPingProbability(
        locatorPosition, lostBotPosition, 1.2
    )

    assert lowAlphaProbability > highAlphaProbability


def testFoundWhenPositionsMatchB():
    # if both bots occupy the same cell then we found the lost bot
    # no reason to keep listening for pings when he's literally here
    locatorPosition = (4, 4)

    detectorResult = runDetectorB(
        locatorPosition, locatorPosition, 0.5
    )

    assert detectorResult == FOUND


def testSameCellProbabilityRejectedB():
    # same-cell detection is handled separately as FOUND
    # the normal ping probability function should not process it
    with pytest.raises(ValueError):
        getPingProbability((1, 1), (1, 1), 0.5)


def testDetectorReproducibilityB():
    # using the same random seed should reproduce the same reading
    # very useful when experiments start acting suspicious
    firstGenerator = random.Random(42)
    secondGenerator = random.Random(42)

    firstReading = runDetectorB(
        (0, 0), (0, 5), 0.4, firstGenerator
    )
    secondReading = runDetectorB(
        (0, 0), (0, 5), 0.4, secondGenerator
    )

    assert firstReading == secondReading
    assert firstReading in (PING, NO_PING)


def testDetectorEmpiricalProbabilityB():
    # this is a statistical sanity check rather than checking one
    # random result. over many readings, the observed ping rate
    # should be reasonably close to the theoretical probability
    locatorPosition = (0, 0)
    lostBotPosition = (0, 4)
    alpha = 0.5
    numTrials = 5000

    randomGenerator = random.Random(123)

    expectedProbability = getPingProbability(
        locatorPosition, lostBotPosition, alpha
    )

    pingCount = 0

    for trial in range(numTrials):
        detectorResult = runDetectorB(
            locatorPosition,
            lostBotPosition,
            alpha,
            randomGenerator
        )

        if detectorResult == PING:
            pingCount += 1

    observedProbability = pingCount / numTrials

    # allowing a small tolerance because randomness is randomness
    assert abs(observedProbability - expectedProbability) < 0.04


def testInvalidAlphaB():
    # alpha cannot be negative, zero, infinite, or nan
    # don't let invalid math sneak into the simulation
    invalidValues = (0, -0.5, float("inf"), float("nan"))

    for alpha in invalidValues:
        with pytest.raises(ValueError):
            runDetectorB((0, 0), (0, 3), alpha)
