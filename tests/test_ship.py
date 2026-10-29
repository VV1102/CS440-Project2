from src.ship import (
    create_grid,
    get_neighbors,
    count_open_neighbors,
    find_dead_ends,
    generate_ship,
)

from src.constants import BLOCKED, OPEN


def test_create_grid():  #this test checks if the grid is created with the correct size with all cells blocked initial
    grid = create_grid(10)

    assert len(grid) == 10
    assert len(grid[0]) == 10

    for row in grid:
        for cell in row:
            assert cell == BLOCKED

#second test checks if the center cell has four up down left right neighbors
def test_center_cell_has_four_neighbors():
    grid = create_grid(5)

    neighbors = get_neighbors(grid, 2, 2)

    assert len(neighbors) == 4

#third test checks if the corner cell has two neighbors
def test_corner_has_two_neighbors():
    grid = create_grid(5)

    neighbors = get_neighbors(grid, 0, 0) #code doesn't go outside the grid

    assert len(neighbors) == 2

def test_count_open_neighbors(): #checks the neighbors count correctly for open cells
    grid = create_grid(5)

    grid[2][2] = OPEN

    assert count_open_neighbors(grid, 2, 1) == 1


def test_generate_ship_size(): #checks if the generated ship has the correct size D X D
    grid = generate_ship(20)

    assert len(grid) == 20

    for row in grid:
        assert len(row) == 20


def test_generated_ship_has_open_cells(): #checks if the ship generated has opened at least one cell
    grid = generate_ship(20)

    open_cells = 0

    for row in grid:
        for cell in row:
            if cell == OPEN:
                open_cells += 1

    assert open_cells > 0

