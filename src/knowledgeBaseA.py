from src.pathfinding import getOpenCells


def initializeKnowledgeBase(grid):
    # At the beginning we don't know where LostBot is
    # So every open cell is a possible location

    openCells = getOpenCells(grid)

    # Store the possible cells in a set
    possibleCells = set(openCells)

    return possibleCells


def updateKnowledgeBase(possibleCells, locatorPosition, k, result):
    # Create a new set to store the remaining possibilities
    updatedCells = set()

    # If the detector found LostBot, the search is complete
    if result == "found":
        return {locatorPosition}

    locatorRow, locatorCol = locatorPosition

    # Check each possible location
    for cell in possibleCells:

        row, col = cell

        # Calculate distance in rows and columns
        rowDistance = abs(locatorRow - row)
        colDistance = abs(locatorCol - col)

        # Check whether the cell is inside the detector square
        insideSquare = rowDistance <= k and colDistance <= k

        if result == "ping":
            # A ping means LostBot must be inside the square
            if insideSquare:
                updatedCells.add(cell)

        elif result == "no ping":
            # No ping means LostBot must be outside the square
            if not insideSquare:
                updatedCells.add(cell)

    # The detector would report "found" if LostBot
    # were at LocatorBot's current position
    updatedCells.discard(locatorPosition)

    return updatedCells
