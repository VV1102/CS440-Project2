def detectorTypeA(locatorPosition, lostBotPosition, k):
    # If both bots are in the same cell, we found LostBot
    if locatorPosition == lostBotPosition:
        return "found"

    # Get the coordinates of both bots
    locatorRow, locatorCol = locatorPosition
    lostRow, lostCol = lostBotPosition

    # Calculate distance between the bots
    rowDistance = abs(locatorRow - lostRow)
    colDistance = abs(locatorCol - lostCol)

    # Check whether LostBot is within the square radius
    if rowDistance <= k and colDistance <= k:
        return "ping"

    return "no ping"
