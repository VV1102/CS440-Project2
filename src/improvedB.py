# Varshini does B content

# Type B: choose informative detector positions while balancing travel cost.
import math
import random
from collections import deque
from src.detectorB import getPingProbability
from src.knowledgeBaseB import updateKnowledgeBaseB
from src.pathfinding import bfs
from src.ship import get_neighbors
from src.constants import OPEN


def getDistanceMapB(grid, startPosition):
    # one BFS gives movement distances to EVERY reachable cell. no repeated bfs spam
    distanceMap = {startPosition: 0}
    cellQueue = deque([startPosition])
    while cellQueue:
        currentPosition = cellQueue.popleft()
        for neighborPosition in get_neighbors(grid, *currentPosition):
            if grid[neighborPosition[0]][neighborPosition[1]] != OPEN or neighborPosition in distanceMap:
                continue
            distanceMap[neighborPosition] = distanceMap[currentPosition] + 1
            cellQueue.append(neighborPosition)
    return distanceMap


def getExpectedInformationGainB(knowledgeBase, detectorPosition, alpha):
    # mutual information = entropy of the detector's outcome minus expected noise
    # FOUND counts as a third outcome; can't just pretend same-cell is a ping
    foundProbability = knowledgeBase.get(detectorPosition, 0.0)
    pingProbability = 0.0
    expectedConditionalEntropy = 0.0
    for cell, probability in knowledgeBase.items():
        if probability <= 0 or cell == detectorPosition:
            continue
        likelihood = getPingProbability(detectorPosition, cell, alpha)
        pingProbability += probability * likelihood
        if 0 < likelihood < 1:
            expectedConditionalEntropy -= probability * (likelihood * math.log2(likelihood) +
                                                         (1 - likelihood) * math.log2(1 - likelihood))
    noPingProbability = max(0.0, 1.0 - foundProbability - pingProbability)
    outcomeEntropy = -sum(value * math.log2(value) for value in
                          (foundProbability, pingProbability, noPingProbability) if value > 0)
    return max(0.0, outcomeEntropy - expectedConditionalEntropy)


def chooseImprovedTargetB(grid, locatorPosition, knowledgeBase, alpha, movementCost=1.0,
                          detectorCost=0.5, maxCandidates=30, rng=None):
    # evaluate high-probability spots AND geographically spread-out spots
    # utility = chance to find it + info gain, discounted by cost of getting there
    if rng is None:
        rng = random
    if movementCost < 0 or detectorCost <= 0:
        raise ValueError("movement cost must be nonnegative and detector cost positive")
    if maxCandidates < 1:
        raise ValueError("maxCandidates must be positive")
    distanceMap = getDistanceMapB(grid, locatorPosition)
    if not distanceMap:
        raise ValueError("no reachable cells")
    rankedCells = sorted(distanceMap, key=lambda cell: knowledgeBase.get(cell, 0.0), reverse=True)
    # when movement is free, every cell is a potential detector position
    if movementCost == 0:
        candidateCells = rankedCells
    else:
        candidateCells = rankedCells[:maxCandidates]
        # always consider current cell and a handful of near cells
        nearbyCells = sorted(distanceMap, key=distanceMap.get)[:maxCandidates]
        candidateCells = list(dict.fromkeys(candidateCells + nearbyCells + [locatorPosition]))
    bestScore = -float("inf")
    bestCells = []
    for cell in candidateCells:
        informationGain = getExpectedInformationGainB(knowledgeBase, cell, alpha)
        discoveryProbability = knowledgeBase.get(cell, 0.0)
        travelCost = movementCost * distanceMap[cell]
        # information has value, but taking 40 steps for a tiny gain is clown behavior
        score = (informationGain + discoveryProbability) / (detectorCost + travelCost)
        if score > bestScore + 1e-12:
            bestScore, bestCells = score, [cell]
        elif abs(score - bestScore) <= 1e-12:
            bestCells.append(cell)
    return rng.choice(bestCells)


def getImprovedMoveB(grid, locatorPosition, knowledgeBase, alpha, movementCost=1.0,
                     detectorCost=0.5, maxCandidates=30, rng=None):
    targetPosition = chooseImprovedTargetB(grid, locatorPosition, knowledgeBase, alpha,
                                           movementCost, detectorCost, maxCandidates, rng)
    path = bfs(grid, locatorPosition, targetPosition)
    return locatorPosition if len(path) == 1 else path[1]


def improvedBStep(grid, locatorPosition, knowledgeBase, detectorResult, alpha,
                  movementCost=1.0, detectorCost=0.5, rng=None):
    # same external interface as baselineBStep, so integration isn't a nightmare
    updatedBeliefs = updateKnowledgeBaseB(knowledgeBase, locatorPosition, detectorResult, alpha)
    if detectorResult == "FOUND":
        return locatorPosition, updatedBeliefs
    nextPosition = getImprovedMoveB(grid, locatorPosition, updatedBeliefs, alpha,
                                    movementCost, detectorCost, rng=rng)
    return nextPosition, updatedBeliefs
