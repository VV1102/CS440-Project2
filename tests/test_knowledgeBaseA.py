from src.knowledgeBaseA import (
    initializeKnowledgeBase,
    updateKnowledgeBase
)


def test_initial_knowledge():
    # 1 = open, 0 = blocked
    grid = [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 1]
    ]

    possibleCells = initializeKnowledgeBase(grid)

    expected = {
        (0, 0),
        (0, 1),
        (1, 1),
        (1, 2),
        (2, 2)
    }

    assert possibleCells == expected


def test_ping_update():
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

    assert updated == {
        (0, 1),
        (1, 0),
        (1, 1)
    }


def test_no_ping_update():
    possibleCells = {
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1), (1, 2),
        (2, 0), (2, 1), (2, 2)
    }

    updated = updateKnowledgeBase(
        possibleCells,
        (0, 0),
        1,
        "no ping"
    )

    assert updated == {
        (0, 2),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2)
    }


def test_found_update():
    possibleCells = {(0, 0), (0, 1), (1, 1)}

    updated = updateKnowledgeBase(
        possibleCells,
        (1, 1),
        1,
        "found"
    )

    assert updated == {(1, 1)}
