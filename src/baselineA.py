import random

from src.detectorA import detectorTypeA #imports the detector A function from the Detector A file
from src.knowledgeBaseA import (
    initializeKnowledgeBase,
    updateKnowledgeBase
)
#import two functions initializeKnowledgeBase and updateKnowledgeBase
from src.pathfinding import bfs


def runBaselineA(grid, locatorPosition, lostBotPosition, k):
    # define the function wit the map, the position of the locator bot, the position of the lost bot and the range of the detector 
    possibleCells = initializeKnowledgeBase(grid)
    #we start with making all open cells possible locations for the lost bot
    moves = 0 #counts how many times the locator bot moves
    detectorActions = 0 #locator uses its detector count

    while True:
        #we do a loop uses the detector to see the lostbot position 
        result = detectorTypeA(
            locatorPosition,
            lostBotPosition,
            k
        ) 
        detectorActions += 1

        # we stop the loop if LostBot has been found
        if result == "found":
            break

        # we update the possible lostbot locations based off the detector feedback
        possibleCells = updateKnowledgeBase(
            possibleCells,
            locatorPosition,
            k,
            result
        )

        # this part finds the nearest cell using BFS 
        nearestCells = []
        shortestDistance = float("inf") #sets shortest dist to infinity so the distance has a value for comparison

        for cell in possibleCells: #goes through each cell 
            path = bfs(grid, locatorPosition, cell) #uses BFS to find the shortest path from Locatorbot to cell

            if path is None:
                continue

            distance = len(path) - 1

            if distance < shortestDistance: 
                shortestDistance = distance
                nearestCells = [cell]
            #checks if the cell is closer than previous closest cell and saves
            elif distance == shortestDistance:
                nearestCells.append(cell)

        #this part checks if the list of reachable cells is empty and raises an error if so
        if not nearestCells:
            raise RuntimeError("No reachable possible LostBot locations")

        # stop with an error no reachable locations
        target = random.choice(nearestCells)
        #random choice from the closest loc
        path = bfs(grid, locatorPosition, target) # find the shortest path toward that target

        # we move one cell forward the path
        locatorPosition = path[1]
        moves += 1

    totalCost = moves + 0.5 * detectorActions
    #calculate the total cost of the search 
    return {
        "moves": moves,
        "detector_actions": detectorActions,
        "total_cost": totalCost,
        "found": True
    }
