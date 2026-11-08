# Varshini does B content

# Bayesian location beliefs for the stationary LostBot.
import math
from src.detectorB import FOUND, PING, NO_PING, getPingProbability
from src.pathfinding import getOpenCells


def initializeKnowledgeBaseB(grid, locatorPosition=None):
    # uniform prior: we know the ship, not where the missing bot wandered off to
    possibleCells = getOpenCells(grid)
    if locatorPosition is not None:
        # only exclude current cell if we've already checked it and know it is empty
        possibleCells = [cell for cell in possibleCells if cell != locatorPosition]
    if not possibleCells:
        raise ValueError("knowledge base needs at least one possible lost-bot cell")
    initialProbability = 1.0 / len(possibleCells)
    return {cell: initialProbability for cell in possibleCells}


def normalizeKnowledgeBaseB(knowledgeBase):
    # normalization is NOT optional; otherwise these aren't probabilities anymore
    if not knowledgeBase:
        raise ValueError("knowledge base cannot be empty")
    if any(not math.isfinite(value) or value < 0 for value in knowledgeBase.values()):
        raise ValueError("probabilities must be finite and nonnegative")
    totalProbability = math.fsum(knowledgeBase.values())
    if totalProbability <= 0:
        raise ValueError("observation has zero probability under the current beliefs")
    return {cell: value / totalProbability for cell, value in knowledgeBase.items()}


def updateKnowledgeBaseB(knowledgeBase, locatorPosition, detectorResult, alpha):
    # Bayes: posterior(cell) proportional to prior(cell) * likelihood(observation | cell)
    # important: FOUND is a terminal observation, not some funky normal ping
    if detectorResult not in (PING, NO_PING, FOUND):
        raise ValueError("unknown detector result")
    if detectorResult == FOUND:
        if locatorPosition not in knowledgeBase:
            raise ValueError("FOUND contradicts the current knowledge base")
        return {cell: float(cell == locatorPosition) for cell in knowledgeBase}
    if not math.isfinite(alpha) or alpha <= 0:
        raise ValueError("alpha must be a finite positive number")
    updatedBeliefs = {}
    for cell, priorProbability in knowledgeBase.items():
        if cell == locatorPosition:
            # detector would say FOUND here, so ping/no-ping rules out this cell
            updatedBeliefs[cell] = 0.0
            continue
        pingProbability = getPingProbability(locatorPosition, cell, alpha)
        observationLikelihood = pingProbability if detectorResult == PING else -math.expm1(-alpha * (math.dist(locatorPosition, cell) - 1.0))
        updatedBeliefs[cell] = priorProbability * observationLikelihood
    return normalizeKnowledgeBaseB(updatedBeliefs)


def excludeVisitedCellB(knowledgeBase, visitedPosition):
    # only call when we KNOW the lost bot isn't there (e.g. detector returned not FOUND)
    updatedBeliefs = dict(knowledgeBase)
    if visitedPosition in updatedBeliefs:
        updatedBeliefs[visitedPosition] = 0.0
    return normalizeKnowledgeBaseB(updatedBeliefs)
