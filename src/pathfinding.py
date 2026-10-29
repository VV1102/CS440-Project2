import random
from collections import deque

from src.constants import OPEN
from src.ship import get_neighbors


def getOpenCells(grid):
    # goes through the whole ship and saves the coordinates of every cell the bot can actually move through

    openCells = []
    # check each position in the grid and add it if its open
    for row in range(len(grid)):
        for col in range(len(grid[row])):

            if grid[row][col] == OPEN:
                openCells.append((row, col))

    return openCells


def bfs(grid, start, goal, forbidden_cells=None):
    # uses breadth first search to find the shortest path from where the bot starts to the button
    # forbidden cells are any cells we want the bot to completely avoid while finding the path

    #if there arent any forbidden cells just make it an empty set so the rest of the search works the same
    if forbidden_cells is None:
        forbidden_cells = set()


    #the queue keeps track of what cells bfs still needs to check
    #visited stops us from going in circles and parent lets us trace the final path backwards later

    queue = deque([start])

    visited = {start}

    parent = {start: None}

    #keep searching as long as there are still cells left to check
    while queue:

        current = queue.popleft()

        #if we made it to the button theres no reason to keep searching
        if current == goal:
            break

        row, col = current
        #look at every cell directly next to the current one
        for neighbor in get_neighbors(grid, row, col):

            neighborRow, neighborCol = neighbor

            #cant move through a wall so skip blocked cells
            if grid[neighborRow][neighborCol] != OPEN:
                continue

            #already checked this one so no need to do it again
            if neighbor in visited:
                continue

            #also skip anything the bot specifically isnt allowed to enter
            if neighbor in forbidden_cells:
                continue

            #this cell is good to explore so save where we came from and add it to the queue

            visited.add(neighbor)

            parent[neighbor] = current

            queue.append(neighbor)

    #if the button never got added to parent then there wasnt any valid path to it
    if goal not in parent:
        return None

    #we found the button so now work backwards through parent to rebuild the shortest path
    path = []

    current = goal
    #start at the button and keep following where each cell came from until we get back to the start

    while current is not None:
        path.append(current)
        current = parent[current]

    #right now the path goes button to start so flip it into the order the bot actually needs
    path.reverse()

    return path


def printPathOnShip(grid, path, start, goal):
    #prints out the ship so we can actually see the shortest path bfs found
    #S is where the bot starts B is the button and * shows the path between them

    #turn the path into a set so its easy to check whether each position belongs to it
    pathCells = set(path) if path else set()

    #go through the whole grid and decide what symbol should be printed at each position
    for row in range(len(grid)):

        line = ""

        for col in range(len(grid[row])):

            position = (row, col)

            if position == start:
                line += "S"

            elif position == goal:
                line += "B"

            elif position in pathCells:
                line += "*"

            elif grid[row][col] == OPEN:
                line += "."

            else:
                line += "#"

        print(line)


if __name__ == "__main__":
    #quick test run so we can generate a ship and actually see bfs find a path on it

    from src.ship import generate_ship

    grid = generate_ship(20)

    #grab two different random open cells to act as the bot start and button

    openCells = getOpenCells(grid)

    start, goal = random.sample(openCells, 2)

    #find the shortest path between the two random positions

    path = bfs(grid, start, goal)

    print("Bot starts at:", start)
    print("Button is at:", goal)

    #print out what bfs found and then show the path directly on the ship

    if path is None:
        print("No path found.")
    else:
        print("Shortest path length:", len(path) - 1)
        print("Path:")
        print(path)

    print()
    printPathOnShip(grid, path, start, goal)
