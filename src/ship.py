import random

from src.constants import BLOCKED, OPEN
#0 means blocked/wall and 1 means open space

def create_grid(D):
    #this function creates a D x D grid made of blocked cells

    grid = []

    for row in range(D):
        newRow = []

        for col in range(D):
            newRow.append(BLOCKED) #adds the row to the grid

        grid.append(newRow)

    return grid #returns the complete grid

def get_neighbors(grid, row, col):
    #this function returns a list of neighboring cell coordinates of up, down, left, and right
    #no diagonals

    D = len(grid)

    directions = [
        (-1, 0),  #goes up
        (1, 0),   #goes down
        (0, -1),  #goes left
        (0, 1)    #goes right
    ]

    neighbors = [] #empty list to store valid neighbors

    for rowChange, colChange in directions:

        newRow = row + rowChange
        newCol = col + colChange

        #make sure the neighbor is still within the grid boundaries

        if 0 <= newRow < D and 0 <= newCol < D:
            neighbors.append((newRow, newCol))

    return neighbors

def count_open_neighbors(grid, row, col):
    #this function counts how many of the neighboring cells are open

    count = 0

    neighbors = get_neighbors(grid, row, col)

    for neighborRow, neighborCol in neighbors:

        if grid[neighborRow][neighborCol] == OPEN:
            count += 1 #goes through each neighbor

    return count

def open_random_interior_cell(grid):

    D = len(grid) #gets the size of the grid

    #randomly chooses a row and a column, none of the outer edge cells would be chosen

    row = random.randint(1, D - 2)
    col = random.randint(1, D - 2)

    grid[row][col] = OPEN #opens the randomly chosen interior cell

    return (row, col)

def find_candidate_cells(grid):
    #this function finds all the blocked cells
    #have exactly one open neighbor cell
    D = len(grid)

    candidates = []

    for row in range(D):
        for col in range(D): #goes through every cell in the grid

            if grid[row][col] == BLOCKED:

                if count_open_neighbors(grid, row, col) == 1:
                    candidates.append((row, col))
    #checks the blocked cells to see if they have exactly one open neighbor and adds them to the candidates list
    return candidates

def grow_maze(grid):
    #this function grows the maze and keeps repeating the process until no more cells can be opened
    while True:

        candidates = find_candidate_cells(grid)

        if len(candidates) == 0:
            break

        chosenRow, chosenCol = random.choice(candidates)
        #randomly choses one cell and opens that cell
        grid[chosenRow][chosenCol] = OPEN

def find_dead_ends(grid):

    D = len(grid) #gets the size of the grid
    deadend = []

    for row in range(D):
        for col in range(D):

            if grid[row][col] == OPEN: #only looks at open cells

                if count_open_neighbors(grid, row, col) == 1: #if the open cell has exactly one open neighbor then it is a dead end
                    deadend.append((row, col)) #adds to the deadend list

    return deadend

def print_ship(grid):
    #this part prints the ship in a readable form so we can see the maze

    for row in grid:

        line = ""

        for cell in row:

            if cell == BLOCKED:
                line += "#" #represents a blocked cell
            else:
                line += "_"  #represents an open cell

        print(line)

def reduce_dead_ends(grid):
    #the goal here is to remove atleast half of the deadends by opening the blocked neighbor cells

    initialDeadend = find_dead_ends(grid) #finds all the deadends and counts them

    initialCount = len(initialDeadend)

    targetCount = initialCount / 2 #target number to make the deadends half

    while True:

        currentDeadend = find_dead_ends(grid)

        # repeat the process until the number of deadends is down to the target
        if len(currentDeadend) <= targetCount:
            break

        # randomly select a current dead end
        dead_end_row, dead_end_col = random.choice(currentDeadend)

        # find the blocked neighbor cells of that dead end
        blockedNeighbors = []

        for neighborRow, neighborCol in get_neighbors(
                grid,
                dead_end_row,
                dead_end_col
        ):
            if grid[neighborRow][neighborCol] == BLOCKED:
                blockedNeighbors.append(
                    (neighborRow, neighborCol)
                )

        #open one random blocked neighbor
        if blockedNeighbors:

            chosenRow, chosenCol = random.choice(
                blockedNeighbors
            )

            grid[chosenRow][chosenCol] = OPEN

def generate_ship(D):
    #we create and return a complete D x D ship combination of all the funcs

    grid = create_grid(D)

    open_random_interior_cell(grid)

    grow_maze(grid)

    reduce_dead_ends(grid)

    return grid

if __name__ == "__main__":

    D = 20

    #run and test
    grid = create_grid(D)
    start = open_random_interior_cell(grid)
    grow_maze(grid)

    before = len(find_dead_ends(grid)) #counts of the og deadcount before reduction

    print("Initial open cell:", start)
    print("Dead ends BEFORE reduction:", before)

    # Reduce dead ends
    reduce_dead_ends(grid)

    after = len(find_dead_ends(grid))

    print("Dead ends AFTER reduction:", after) #counts again to verify reduction

    print("\nFinal Ship:")
    print_ship(grid)