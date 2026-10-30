import math
import random
from src.pathfinding import bfs, getOpenCells

from src.detectorA import detectorTypeA
from src.knowledgeBaseA import (
    initializeKnowledgeBase,
    updateKnowledgeBase
)

def calculateInformationGain(possibleCells, scanPosition, k):
    # Count how many possible LostBot locations
    # are inside the detector's square

    if len(possibleCells) == 0:
        return 0

    scanRow, scanCol = scanPosition
    insideCount = 0

    for row, col in possibleCells:

        rowDistance = abs(scanRow - row)
        colDistance = abs(scanCol - col)

        if rowDistance <= k and colDistance <= k:
            insideCount += 1

    # Calculate the probability of getting a ping
    # Assuming all remaining cells are equally likely
    probability = insideCount / len(possibleCells)

    # No information gain if every possible
    # location gives the same result
    if probability == 0 or probability == 1:
        return 0

    # Binary entropy measures how informative
    # the detector result is expected to be
    informationGain = (
        -probability * math.log2(probability)
        - (1 - probability) * math.log2(1 - probability)
    )

    return informationGain

def chooseBestScanPosition(grid, locatorPosition, possibleCells, k):
    # Get all open cells where LocatorBot could scan
    openCells = getOpenCells(grid)

    bestPositions = []
    bestScore = float("-inf")

    # Evaluate every possible scanning location
    for position in openCells:

        # Find shortest path to this location
        path = bfs(grid, locatorPosition, position)

        if path is None:
            continue

        # Calculate how much moving would cost
        distance = len(path) - 1

        # Calculate expected information gain
        informationGain = calculateInformationGain(
            possibleCells, position, k
        )

        # Prefer informative scans that are closer
        score = informationGain / (distance + 0.5)

        if score > bestScore + 1e-10:
            bestScore = score
            bestPositions = [position]

        elif abs(score - bestScore) <= 1e-10:
            bestPositions.append(position)

    if not bestPositions:
        return None

    return random.choice(bestPositions)

def runImprovedA(grid, locatorPosition, lostBotPosition, k):
    # Start with all open cells as possible LostBot locations
    possibleCells = initializeKnowledgeBase(grid)

    moves = 0
    detectorActions = 0

    # Remember cells where we have already scanned
    checkedPositions = set()

    while True:
        # Run the detector at the current location
        result = detectorTypeA(
            locatorPosition,
            lostBotPosition,
            k
        )
        detectorActions += 1

        # Stop when LostBot is found
        if result == "found":
            break

        # Update the knowledge base
        possibleCells = updateKnowledgeBase(
            possibleCells,
            locatorPosition,
            k,
            result
        )

        checkedPositions.add(locatorPosition)

        if not possibleCells:
            raise RuntimeError("No possible LostBot locations remain")

        # Choose an informative scanning position
        target = chooseBestScanPosition(
            grid,
            locatorPosition,
            possibleCells,
            k
        )

        # If no useful scanning position exists,
        # directly search the nearest possible cell
        bestGain = calculateInformationGain(
            possibleCells, target, k
        ) if target is not None else 0

        if bestGain <= 0 or target == locatorPosition:
            nearestDistance = float("inf")
            nearestCells = []

            for cell in possibleCells:
                path = bfs(grid, locatorPosition, cell)

                if path is None:
                    continue

                distance = len(path) - 1

                if distance < nearestDistance:
                    nearestDistance = distance
                    nearestCells = [cell]

                elif distance == nearestDistance:
                    nearestCells.append(cell)

            if not nearestCells:
                raise RuntimeError("No reachable LostBot candidates")

            target = random.choice(nearestCells)

        # Travel toward the target
        path = bfs(grid, locatorPosition, target)

        if path is None or len(path) < 2:
            raise RuntimeError("Unable to make progress")

        # Move one cell along the BFS path
        locatorPosition = path[1]
        moves += 1

    return {
        "moves": moves,
        "detector_actions": detectorActions,
        "total_cost": moves + 0.5 * detectorActions,
        "found": True
    }
