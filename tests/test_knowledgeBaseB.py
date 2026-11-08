# Varshini does B content


import math
import pytest

from src.detectorB import PING, NO_PING, FOUND

from src.knowledgeBaseB import (
    initializeKnowledgeBaseB,
    normalizeKnowledgeBaseB,
    updateKnowledgeBaseB,
    excludeVisitedCellB
)


def testUniformInitializationB():
    # at the beginning we have no clue where the lost bot is
    # so every possible open cell gets the same probability
    grid = [
        [1, 1, 0],
        [1, 0, 1],
        [1, 1, 1]
    ]

    knowledgeBase = initializeKnowledgeBaseB(grid)

    assert len(knowledgeBase) == 7
    assert sum(knowledgeBase.values()) == pytest.approx(1.0)

    for probability in knowledgeBase.values():
        assert probability == pytest.approx(1 / 7)


def testBlockedCellsExcludedB():
    # blocked cells should never be possible lost bot locations
    # bro cannot be chilling inside a wall
    grid = [
        [1, 0, 1],
        [0, 1, 0]
    ]

    knowledgeBase = initializeKnowledgeBaseB(grid)

    assert set(knowledgeBase.keys()) == {
        (0, 0),
        (0, 2),
        (1, 1)
    }


def testKnownEmptyStartingCellExcludedB():
    # if we already confirmed our starting cell is empty,
    # there is no reason to assign probability to that location
    grid = [[1, 1, 1]]

    knowledgeBase = initializeKnowledgeBaseB(
        grid, locatorPosition=(0, 0)
    )

    assert (0, 0) not in knowledgeBase
    assert knowledgeBase[(0, 1)] == pytest.approx(0.5)
    assert knowledgeBase[(0, 2)] == pytest.approx(0.5)


def testNormalizeProbabilitiesB():
    # normalization should preserve the relative weights while
    # making sure the entire distribution adds up to 1
    knowledgeBase = {
        (0, 0): 2.0,
        (0, 1): 3.0,
        (0, 2): 5.0
    }

    normalizedBeliefs = normalizeKnowledgeBaseB(knowledgeBase)

    assert normalizedBeliefs[(0, 0)] == pytest.approx(0.2)
    assert normalizedBeliefs[(0, 1)] == pytest.approx(0.3)
    assert normalizedBeliefs[(0, 2)] == pytest.approx(0.5)
    assert sum(normalizedBeliefs.values()) == pytest.approx(1.0)


def testPingFavorsNearbyCellsB():
    # a ping should make closer locations more likely
    # assuming they had equal prior probabilities
    knowledgeBase = {
        (0, 1): 0.5,
        (0, 5): 0.5
    }

    updatedBeliefs = updateKnowledgeBaseB(
        knowledgeBase, (0, 0), PING, 0.7
    )

    assert updatedBeliefs[(0, 1)] > updatedBeliefs[(0, 5)]
    assert sum(updatedBeliefs.values()) == pytest.approx(1.0)


def testNoPingEliminatesAdjacentCellB():
    # adjacent cells ALWAYS produce a ping according to the formula
    # so if we get NO_PING, that adjacent cell cannot contain the bot
    knowledgeBase = {
        (0, 1): 0.5,
        (0, 4): 0.5
    }

    updatedBeliefs = updateKnowledgeBaseB(
        knowledgeBase, (0, 0), NO_PING, 0.5
    )

    assert updatedBeliefs[(0, 1)] == pytest.approx(0.0)
    assert updatedBeliefs[(0, 4)] == pytest.approx(1.0)


def testBayesianPingCalculationB():
    # manually checking Bayes rule so we know the update is
    # mathematically correct, not just giving reasonable-looking numbers
    knowledgeBase = {
        (0, 1): 0.4,
        (0, 3): 0.6
    }

    alpha = 0.5

    firstLikelihood = 1.0
    secondLikelihood = math.exp(-alpha * (3 - 1))

    totalLikelihood = (
            0.4 * firstLikelihood +
            0.6 * secondLikelihood
    )

    expectedFirstPosterior = (
            0.4 * firstLikelihood / totalLikelihood
    )

    updatedBeliefs = updateKnowledgeBaseB(
        knowledgeBase, (0, 0), PING, alpha
    )

    assert updatedBeliefs[(0, 1)] == pytest.approx(
        expectedFirstPosterior
    )


def testBayesianNoPingCalculationB():
    # same idea as the previous test but using the complement
    # of ping probability for a negative detector reading
    knowledgeBase = {
        (0, 2): 0.5,
        (0, 4): 0.5
    }

    alpha = 0.5

    firstLikelihood = 1 - math.exp(-alpha * (2 - 1))
    secondLikelihood = 1 - math.exp(-alpha * (4 - 1))

    expectedFirstPosterior = (
            0.5 * firstLikelihood /
            (0.5 * firstLikelihood + 0.5 * secondLikelihood)
    )

    updatedBeliefs = updateKnowledgeBaseB(
        knowledgeBase, (0, 0), NO_PING, alpha
    )

    assert updatedBeliefs[(0, 2)] == pytest.approx(
        expectedFirstPosterior
    )


def testFoundCollapsesDistributionB():
    # FOUND means uncertainty is gone. probability becomes 1
    # at the discovered location and zero everywhere else
    knowledgeBase = {
        (0, 0): 0.2,
        (0, 1): 0.3,
        (0, 2): 0.5
    }

    updatedBeliefs = updateKnowledgeBaseB(
        knowledgeBase, (0, 1), FOUND, 0.5
    )

    assert updatedBeliefs[(0, 1)] == pytest.approx(1.0)
    assert updatedBeliefs[(0, 0)] == pytest.approx(0.0)
    assert updatedBeliefs[(0, 2)] == pytest.approx(0.0)


def testOrdinaryReadingExcludesCurrentCellB():
    # if we received an ordinary ping rather than FOUND,
    # the lost bot cannot be occupying our current location
    knowledgeBase = {
        (0, 0): 0.3,
        (0, 2): 0.7
    }

    updatedBeliefs = updateKnowledgeBaseB(
        knowledgeBase, (0, 0), PING, 0.4
    )

    assert updatedBeliefs[(0, 0)] == pytest.approx(0.0)
    assert updatedBeliefs[(0, 2)] == pytest.approx(1.0)


def testVisitedCellExclusionB():
    # once we confirm a location is empty, remove its probability
    # and redistribute the remaining mass across possible cells
    knowledgeBase = {
        (0, 0): 0.2,
        (0, 1): 0.3,
        (0, 2): 0.5
    }

    updatedBeliefs = excludeVisitedCellB(
        knowledgeBase, (0, 0)
    )

    assert updatedBeliefs[(0, 0)] == 0
    assert updatedBeliefs[(0, 1)] == pytest.approx(0.375)
    assert updatedBeliefs[(0, 2)] == pytest.approx(0.625)


def testRepeatedObservationsRemainNormalizedB():
    # repeated Bayesian updates should not gradually destroy
    # the probability distribution due to numerical errors
    knowledgeBase = {
        (0, 2): 0.25,
        (0, 3): 0.25,
        (0, 4): 0.25,
        (0, 5): 0.25
    }

    detectorResults = [PING, NO_PING, PING, NO_PING]

    for detectorResult in detectorResults:
        knowledgeBase = updateKnowledgeBaseB(
            knowledgeBase,
            (0, 0),
            detectorResult,
            0.4
        )

        assert sum(knowledgeBase.values()) == pytest.approx(1.0)
        assert all(
            probability >= 0
            for probability in knowledgeBase.values()
        )


def testImpossibleObservationRejectedB():
    # if a detector reading has literally zero probability
    # under every remaining hypothesis, that's contradictory evidence
    knowledgeBase = {(0, 1): 1.0}

    with pytest.raises(ValueError):
        updateKnowledgeBaseB(
            knowledgeBase, (0, 0), NO_PING, 0.5
        )


def testInvalidDistributionRejectedB():
    # negative probabilities and nan should never be normalized
    invalidDistributions = [
        {(0, 0): -0.5, (0, 1): 1.5},
        {(0, 0): float("nan")},
        {(0, 0): 0.0}
    ]

    for knowledgeBase in invalidDistributions:
        with pytest.raises(ValueError):
            normalizeKnowledgeBaseB(knowledgeBase)
