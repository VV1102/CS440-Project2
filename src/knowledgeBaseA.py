from src.pathfinding import getOpenCells


def initializeKnowledgeBase(grid):
    #we get all the open cells in the grid where the Lostbot could be  

    openCells = getOpenCells(grid)

    # then we store the possible cells in a set
    posCells = set(openCells)

    return posCells


def updateKnowledgeBase(possibleCells, locatorPosition, k, result):
    # this part creates a new set to store the remaining possibilities
    updatedCells = set()

    # so if the detector found LostBot, then the search is complete
    if result == "found":
        return {locatorPosition}

    locRow, locCol = locatorPosition

    # we go through each possible location
    for cell in possibleCells:

        row, col = cell

        # we calculate distance in rows and columns
        rowDistance = abs(locRow - row)
        colDistance = abs(locCol - col)

        # this part checks whether the cell is inside the detector range
        insSquare = rowDistance <= k and colDistance <= k

        if result == "ping":
            # a ping means LostBot must be inside the square
            if insSquare:
                updatedCells.add(cell)

        elif result == "no ping":
            # no ping means LostBot is outside the square
            if not insSquare:
                updatedCells.add(cell)

    #we remove the locatorbots current position from the set since lostbot isn't there
    updatedCells.discard(locatorPosition)

    return updatedCells
