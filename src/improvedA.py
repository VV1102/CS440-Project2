import math
import random
from src.pathfinding import bfs, getOpenCells

from src.detectorA import detectorTypeA
from src.knowledgeBaseA import (
    initializeKnowledgeBase,
    updateKnowledgeBase
) #get all the imports 

def calculateInfoGain(possibleLoc, scanPosition, k):
    # we check if there are any possible locations left for the lostbot

    if len(possibleLoc) == 0:
        return 0 #if not 0
    #this part gets the row and column of the scan position
    currentrow, currentCol = scanPosition
    insideCount = 0
    
    for row, col in possibleLoc:
        #we find how far the cell is from the scan position
        rowDist = abs(currentrow - row)
        colDist = abs(currentCol - col)
        #counts the cells within the detector range
        if rowDist <= k and colDist <= k:
            insideCount += 1

    #probability of a ping
    prob = insideCount / len(possibleLoc)

    #no info is gained if zero
    if prob == 0 or prob == 1:
        return 0

    # we calc information gain using the binary entropy formula
    infoGain = (
        -prob * math.log2(prob)
        - (1 - prob) * math.log2(1 - prob)
    )

    return infoGain

def chooseBestPosition(grid, locatorPosition, possibleCells, k):
    # we get all open cells where locatorbot could scan
    openCells = getOpenCells(grid)
    #okay we store the best positions and score for comparison
    bestPos = []
    bestScore = float("-inf")

    # we check every possible scanning location
    for position in openCells:

        # this part finds shortest path to this cell
        path = bfs(grid, locatorPosition, position)

        if path is None:
            continue

        # this calculate how much moving would cost
        distance = len(path) - 1

        # this part calculates expected information gain
        infoGain = calculateInfoGain(
            possibleCells, position, k
        )
 
        score = infoGain / (distance + 0.5)
        #save the best score and position 
        if score > bestScore + 1e-10:
            bestScore = score
            bestPos = [position]
        #we keep the other positions that have the samr score
        elif abs(score - bestScore) <= 1e-10:
            bestPos.append(position)

    if not bestPos:
        return None

    return random.choice(bestPos) #random choice

def runImprovedA(grid, locatorPosition, lostBotPosition, k):
    # open cells as possible LostBot locations
    possibleCells = initializeKnowledgeBase(grid)
    # we keep track of moves and detector actions
    moves = 0
    detActions = 0

    checkedPositions = set()

    while True:
        # keep looping until LostBot is found
        result = detectorTypeA(
            locatorPosition,
            lostBotPosition,
            k
        )
        detActions += 1

        # we stop when LostBot is found
        if result == "found":
            break

        # then update the knowledge base
        possibleCells = updateKnowledgeBase(
            possibleCells,
            locatorPosition,
            k,
            result
        )

        checkedPositions.add(locatorPosition)

        if not possibleCells:
            raise RuntimeError("None possible LostBot locations left")

        # we select the best position to scan next
        target = chooseBestPosition(
            grid,
            locatorPosition,
            possibleCells,
            k
        )

        # checks how much info the chosen position would give us
        bestGain = calculateInfoGain(
            possibleCells, target, k
        ) if target is not None else 0
        #so if the scan isn't useful or we there alr, we go to the nearest lostbot loc
        if bestGain <= 0 or target == locatorPosition:
            nearestDist = float("inf")
            nearestCells = []

            for cell in possibleCells:
                path = bfs(grid, locatorPosition, cell)

                if path is None:
                    continue
                #calc the distance to the location
                distance = len(path) - 1

                if distance < nearestDist:
                    nearestDist = distance
                    nearestCells = [cell]

                elif distance == nearestDist:
                    nearestCells.append(cell)

            if not nearestCells:
                raise RuntimeError("None reachable LostBot candidates")
            #if none of locations are reachable we error
            target = random.choice(nearestCells)

        # shortest path toward the target
        path = bfs(grid, locatorPosition, target)

        if path is None or len(path) < 2:
            raise RuntimeError("Unable progress")

        # we move one cell along the BFS path
        locatorPosition = path[1]
        moves += 1

    return {
        "moves": moves,
        "detector_actions": detActions,
        "total_cost": moves + 0.5 * detActions,
        "found": True
    }
