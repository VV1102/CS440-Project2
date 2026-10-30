import random

from src.detectorA import detectorTypeA
from src.knowledgeBaseA import (
    initializeKnowledgeBase,
    updateKnowledgeBase
)
from src.pathfinding import bfs


def runBaselineA(grid, locatorPosition, lostBotPosition, k):
    # Start with all open cells as possible locations
    possibleCells = initializeKnowledgeBase(grid)

    # Count the actions to calculate total cost
    moves = 0
    detectorActions = 0

    while True:
        # Run the detector at the current position
        result = detectorTypeA(
            locatorPosition,
            lostBotPosition,
            k
        )
        detectorActions += 1

        # Stop if LostBot has been found
        if result == "found":
            break

        # Update possible locations based on detector feedback
        possibleCells = updateKnowledgeBase(
            possibleCells,
            locatorPosition,
            k,
            result
        )

        # Find the nearest possible cell using BFS distance
        nearestCells = []
        shortestDistance = float("inf")

        for cell in possibleCells:
            path = bfs(grid, locatorPosition, cell)

            if path is None:
                continue

            distance = len(path) - 1

            if distance < shortestDistance:
                shortestDistance = distance
                nearestCells = [cell]

            elif distance == shortestDistance:
                nearestCells.append(cell)

        # Something went wrong if no candidate is reachable
        if not nearestCells:
            raise RuntimeError("No reachable possible LostBot locations")

        # Break ties randomly as required by the baseline
        target = random.choice(nearestCells)

        # Find the shortest path toward that target
        path = bfs(grid, locatorPosition, target)

        # Move one cell along the path
        locatorPosition = path[1]
        moves += 1

    totalCost = moves + 0.5 * detectorActions

    return {
        "moves": moves,
        "detector_actions": detectorActions,
        "total_cost": totalCost,
        "found": True
    }
