# Varshini does B content

# type B detector: probabilistic pings, not maze-distance pings.
import math
import random

PING = "PING"
NO_PING = "NO_PING"
FOUND = "FOUND"


def getEuclideanDistance(firstPosition, secondPosition):
    # walls don't matter for the signal, this is straight-line distance fr
    return math.dist(firstPosition, secondPosition)


def getPingProbability(locatorPosition, lostBotPosition, alpha):
    # alpha must be positive. larger alpha = signal dies faster with distance
    if not math.isfinite(alpha) or alpha <= 0:
        raise ValueError("alpha must be a finite positive number")
    if locatorPosition == lostBotPosition:
        # same cell gives FOUND instead of a normal ping, so don't use this likelihood
        raise ValueError("same-cell detection returns FOUND, not a ping probability")
    distance = getEuclideanDistance(locatorPosition, lostBotPosition)
    return math.exp(-alpha * (distance - 1.0))


def runDetectorB(locatorPosition, lostBotPosition, alpha, rng=None):
    # found means we're literally standing on the lost bot. mission accomplished lol
    if not math.isfinite(alpha) or alpha <= 0:
        raise ValueError("alpha must be a finite positive number")
    if locatorPosition == lostBotPosition:
        return FOUND
    if rng is None:
        rng = random
    pingProbability = getPingProbability(locatorPosition, lostBotPosition, alpha)
    return PING if rng.random() < pingProbability else NO_PING
