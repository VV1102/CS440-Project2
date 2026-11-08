import math
import random
from src.pathfinding import bfs, getOpenCells

from src.detectorA import detectorTypeA
from src.knowledgeBaseA import (
    initializeKnowledgeBase,
    updateKnowledgeBase
) #get all the imports 

def calculateInformationGain(possibleCells, scanPosition, k):
    # we check if there are any possible locations left for the lostbot

    if len(possibleCells) == 0:
        return 0 #if not 0
    #this part gets the row and column of the scan position
    scanRow, scanCol = scanPosition
    insideCount = 0
    
    for row, col in possibleCells:
        #we find how far the cell is from the scan position
        rowDistance = abs(scanRow - row)
        colDistance = abs(scanCol - col)
        #counts the cells within the detector range
        if rowDistance <= k and colDistance <= k:
            insideCount += 1

    #probability of a ping
    probability = insideCount / len(possibleCells)

    #no info is gained if zero
    if probability == 0 or probability == 1:
        return 0

    # we calc information gain using the binary entropy formula
    informationGain = (
        -probability * math.log2(probability)
        - (1 - probability) * math.log2(1 - probability)
    )

    return informationGain

def chooseBestScanPosition(grid, locatorPosition, possibleCells, k):
    # we get all open cells where locatorbot could scan
    openCells = getOpenCells(grid)
    #okay we store the best positions and score for comparison
    bestPositions = []
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
        informationGain = calculateInformationGain(
            possibleCells, position, k
        )
 
        score = informationGain / (distance + 0.5)
        #save the best score and position 
        if score > bestScore + 1e-10:
            bestScore = score
            bestPositions = [position]
        #we keep the other positions that have the samr score
        elif abs(score - bestScore) <= 1e-10:
            bestPositions.append(position)

    if not bestPositions:
        return None

    return random.choice(bestPositions) #random choice

def runImprovedA(grid, locatorPosition, lostBotPosition, k):
    # open cells as possible LostBot locations
    possibleCells = initializeKnowledgeBase(grid)
    # we keep track of moves and detector actions
    moves = 0
    detectorActions = 0

    checkedPositions = set()

    while True:
        # keep looping until LostBot is found
        result = detectorTypeA(
            locatorPosition,
            lostBotPosition,
            k
        )
        detectorActions += 1

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
            raise RuntimeError("No possible LostBot locations remain")

        # we select the best position to scan next
        target = chooseBestScanPosition(
            grid,
            locatorPosition,
            possibleCells,
            k
        )

        # checks how much info the chosen position would give us
        bestGain = calculateInformationGain(
            possibleCells, target, k
        ) if target is not None else 0
        #so if the scan isn't useful or we there alr, we go to the nearest lostbot loc
        if bestGain <= 0 or target == locatorPosition:
            nearestDistance = float("inf")
            nearestCells = []

            for cell in possibleCells:
                path = bfs(grid, locatorPosition, cell)

                if path is None:
                    continue
                #calc the distance to the location
                distance = len(path) - 1

                if distance < nearestDistance:
                    nearestDistance = distance
                    nearestCells = [cell]

                elif distance == nearestDistance:
                    nearestCells.append(cell)

            if not nearestCells:
                raise RuntimeError("No reachable LostBot candidates")
            #if none of locations are reachable we error
            target = random.choice(nearestCells)

        # shortest path toward the target
        path = bfs(grid, locatorPosition, target)

        if path is None or len(path) < 2:
            raise RuntimeError("Unable to make progress")

        # we move one cell along the BFS path
        locatorPosition = path[1]
        moves += 1

    return {
        "moves": moves,
        "detector_actions": detectorActions,
        "total_cost": moves + 0.5 * detectorActions,
        "found": True
    }
