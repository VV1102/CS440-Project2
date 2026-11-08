def detectorTypeA(locatorPosition, lostBotPosition, k):
    # this section sees if both bots are in the same cell it means that we found the LostBot
    if locatorPosition == lostBotPosition:
        return "found"

    # this part gets the coordinates of both bots
    locR, locC = locatorPosition
    lostRow, lostCol = lostBotPosition

    # we calculate distance between the bots
    rowDist = abs(locR - lostRow)
    colDist = abs(locC - lostCol)

    # this part Checks whether LostBot is within the square radius
    if rowDist <= k and colDist <= k: 
        return "ping"

    return "no ping" #lostbot is outside the square radius
