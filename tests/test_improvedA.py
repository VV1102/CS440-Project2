import pytest
from src.pathfinding import bfs
from src.improvedA import calculateInfoGain
from src.improvedA import chooseBestPosition
from src.improvedA import runImprovedA 

def test_balanced_scan():
    possibleCells = {
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3)
    }
#this tests when the lostbot is in the middle of the detector range
    result = calculateInfoGain(
        possibleCells,
        (0, 0),
        1
    )

    # two cells inside, two outside
    # info gain  = 1
    assert result == pytest.approx(1.0)

#tests when all possible cells are inside the detector range
def test_no_information():
    possibleCells = {
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1)
    }

    result = calculateInfoGain(
        possibleCells,
        (0, 0),
        2
    )

    # this means all candidates are inside the detector range
    assert result == 0

def test_choose_valid_position(): #this part tests if the chosen position is valid 
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]
    #all open cells are valid positions to scan
    possibleCells = {
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1), (1, 2),
        (2, 0), (2, 1), (2, 2)
    }

    result = chooseBestPosition(
        grid, (0, 0), possibleCells, 1
    )
    #checks that the selected position is in the possible cell
    assert result in possibleCells

#this tests if the chosen position is reachable from the locator's current position
def test_choose_reachable_position():
    grid = [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 1]
    ]
    #stores the possible loc
    possibleCells = {
        (0, 0), (0, 1),
        (1, 1), (1, 2), (2, 2)
    }

    result = chooseBestPosition(
        grid, (0, 0), possibleCells, 1
    )

    assert result is not None #check if scanning position was found
    assert bfs(grid, (0, 0), result) is not None #check if BFS can find a path to the position

#this tests when lostbot is in the same position as the locator
def test_improved_same_start():
    grid = [
        [1, 1],
        [1, 1]
    ]

    result = runImprovedA(grid, (0, 0), (0, 0), 1)
#lost bot is found immediately, so moves = 0
    assert result["found"] is True
    assert result["moves"] == 0
    assert result["detector_actions"] == 1

#this tests whrn lostbot is far away from the locator
def test_improved_far_bot():
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    result = runImprovedA(grid, (0, 0), (2, 2), 1)

    assert result["found"] is True
    assert result["total_cost"] == (
        result["moves"] + 0.5 * result["detector_actions"]
    )

#tests when the detector range is zero
def test_improved_zero_radius():
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    result = runImprovedA(grid, (0, 0), (2, 2), 0)
#lostbot can still be found or not
    assert result["found"] is True
