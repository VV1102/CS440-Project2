def detectorTypeA(locatorPosition, lostBotPosition, k):
    # this section sees if both bots are in the same cell it means that we found the LostBot
    if locatorPosition == lostBotPosition:
        return "found"

    # this part gets the coordinates of both bots
    locatorRow, locatorCol = locatorPosition
    lostRow, lostCol = lostBotPosition

    # we calculate distance between the bots
    rowDistance = abs(locatorRow - lostRow)
    colDistance = abs(locatorCol - lostCol)

    # this part Checks whether LostBot is within the square radius
    if rowDistance <= k and colDistance <= k: 
        return "ping"

    return "no ping" #lostbot is outside the square radius
