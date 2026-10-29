from src.constants import BLOCKED, OPEN
from src.pathfinding import bfs


def testBfsStraightPath():

    #make the top row completely open so theres one super obvious shortest path for bfs to find
    grid = [
        [OPEN, OPEN, OPEN],
        [BLOCKED, BLOCKED, OPEN],
        [OPEN, OPEN, OPEN],
    ]

    path = bfs(grid, (0, 0), (0, 2))

    #should just go straight across from start to goal, no reason for bfs to take some longer route
    assert path == [
        (0, 0),
        (0, 1),
        (0, 2),
    ]


def testBfsAroundWall():

    #put a wall between the start and goal so bfs is forced to actually find a way around it
    grid = [
        [OPEN, BLOCKED, OPEN],
        [OPEN, BLOCKED, OPEN],
        [OPEN, OPEN, OPEN],
    ]

    path = bfs(grid, (0, 0), (0, 2))

    #only way across is going all the way down around the wall and then coming back up
    #so the path should follow that exact route
    assert path == [
        (0, 0),
        (1, 0),
        (2, 0),
        (2, 1),
        (2, 2),
        (1, 2),
        (0, 2),
    ]


def testBfsNoPath():

    #this wall cuts the grid completely in half so theres genuinely no way to reach the other side
    grid = [
        [OPEN, BLOCKED, OPEN],
        [OPEN, BLOCKED, OPEN],
        [OPEN, BLOCKED, OPEN],
    ]

    path = bfs(grid, (0, 0), (0, 2))

    #bfs should eventually run out of places to search and give back None instead of making up a path
    assert path is None


def testBfsAvoidsForbiddenCell():

    #everything is open here but were manually making the obvious middle cell off limits
    #this makes sure forbidden cells actually affect which route bfs is allowed to use
    grid = [
        [OPEN, OPEN, OPEN],
        [OPEN, OPEN, OPEN],
        [OPEN, OPEN, OPEN],
    ]

    forbidden = {(0, 1)}

    path = bfs(
        grid,
        (0, 0),
        (0, 2),
        forbidden_cells=forbidden,
    )

    #there should still be another way to the goal, it just better not sneak through the forbidden cell
    assert path is not None
    assert (0, 1) not in path