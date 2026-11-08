# Varshini does B content


# Professor's Type B baseline: detect, update, target highest posterior.
import random
from src.pathfinding import bfs
from src.knowledgeBaseB import updateKnowledgeBaseB


def chooseBaselineTargetB(grid, locatorPosition, knowledgeBase, rng=None):
    # highest probability first, then shortest WALKABLE distance, then random tie
    if rng is None:
        rng = random
    bestProbability = max(knowledgeBase.values())
    if bestProbability <= 0:
        raise ValueError("no possible lost-bot locations remain")
    candidateCells = [cell for cell, probability in knowledgeBase.items()
                      if abs(probability - bestProbability) <= 1e-12]
    bestDistance = float("inf")
    bestCells = []
    for cell in candidateCells:
        path = bfs(grid, locatorPosition, cell)
        if path is None:
            continue
        pathDistance = len(path) - 1
        if pathDistance < bestDistance:
            bestDistance = pathDistance
            bestCells = [cell]
        elif pathDistance == bestDistance:
            bestCells.append(cell)
    if not bestCells:
        raise ValueError("no highest-probability target is reachable")
    return rng.choice(bestCells)


def getBaselineMoveB(grid, locatorPosition, knowledgeBase, rng=None):
    # move ONE cell per action, never teleport to the max-probability cell
    targetPosition = chooseBaselineTargetB(grid, locatorPosition, knowledgeBase, rng)
    path = bfs(grid, locatorPosition, targetPosition)
    return locatorPosition if len(path) == 1 else path[1]


def baselineBStep(grid, locatorPosition, knowledgeBase, detectorResult, alpha, rng=None):
    # simulator calls the detector first, then gives us the observation here
    if detectorResult == "FOUND":
        return locatorPosition, updateKnowledgeBaseB(knowledgeBase, locatorPosition, detectorResult, alpha)
    updatedBeliefs = updateKnowledgeBaseB(knowledgeBase, locatorPosition, detectorResult, alpha)
    return getBaselineMoveB(grid, locatorPosition, updatedBeliefs, rng), updatedBeliefs
