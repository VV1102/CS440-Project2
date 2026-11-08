from src.baselineA import runBaselineA


def test_same_start(): 
    #this tests when the locator and lostbot start in the same position
    grid = [
        [1, 1],
        [1, 1]
    ]

    result = runBaselineA(grid, (0, 0), (0, 0), 1)
    #lostbot is found immediately, so moves = 0
    assert result["found"] is True
    assert result["moves"] == 0 
    assert result["detector_actions"] == 1 #only one action happens to find the lostbot
    assert result["total_cost"] == 0.5


def test_adjacent_bot(): 
    #this tests when the lostbot is one cell away from the locator
    grid = [
        [1, 1],
        [1, 1]
    ]

    result = runBaselineA(grid, (0, 0), (0, 1), 1)

    assert result["found"] is True #checks the lost is found
    assert result["total_cost"] == ( #checks the total cost is right
        result["moves"] + 0.5 * result["detector_actions"]
    )

#this tests when the lostbot is far away 
def test_far_bot():
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    result = runBaselineA(grid, (0, 0), (2, 2), 1)

    assert result["found"] is True
    assert result["moves"] >= 1 #one move needed

#this tests when the detector range is zero
def test_zero_radius():
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    result = runBaselineA(grid, (0, 0), (2, 2), 0)
#checks if lostbot is still ablr to be found 
    assert result["found"] is True
