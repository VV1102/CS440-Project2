from src.knowledgeBaseA import (
    initializeKnowledgeBase,
    updateKnowledgeBase
)


def test_initial_knowledge():
    #this part tests if the knowledge base is initialized correctly with the open cells
    # 1 = open and 0 = blocked
    grid = [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 1]
    ]

    possibleCells = initializeKnowledgeBase(grid)
    #these are the open cells in the grid 
    expected = {
        (0, 0),
        (0, 1),
        (1, 1),
        (1, 2),
        (2, 2)
    }

    assert possibleCells == expected #making sure only open cells are here


def test_ping_update(): #tests if a ping keeps only the cells within the detector range
    possibleCells = {
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1), (1, 2),
        (2, 0), (2, 1), (2, 2)
    }
 
    updated = updateKnowledgeBase( 
        possibleCells,
        (0, 0),
        1,
        "ping"
    )
#we check that only the cells within the detector range are kept
    assert updated == {
        (0, 1),
        (1, 0),
        (1, 1)
    }
#removes the current pos if lost is not found

def test_no_ping_update(): #this tests if no ping, cells outside the detector range are kept
    possibleCells = {
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1), (1, 2),
        (2, 0), (2, 1), (2, 2)
    }
    #update possible cells with no ping result
    updated = updateKnowledgeBase(
        possibleCells,
        (0, 0),
        1,
        "no ping"
    )
    #checks that only the cells outside the range
    assert updated == {
        (0, 2),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2)
    }

#tests if detector finds the lostbot
def test_found_update():
    possibleCells = {(0, 0), (0, 1), (1, 1)}

    updated = updateKnowledgeBase(
        possibleCells,
        (1, 1),
        1,
        "found"
    )

    assert updated == {(1, 1)}
