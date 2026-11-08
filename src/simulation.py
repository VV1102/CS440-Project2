# Varshini & Sri will write together once all dependent parts are done


# Varshini does simulation content

#Runs complete LocatorBot searches for both detector types and both strategies.

#The simulator handles the actual search process while the separate A and B files
#handle detection, knowledge-base updates, and choosing where the bot should go.
# Keeping these responsibilities separate makes the experiment comparisons fairer.


import math
import random

from src.constants import OPEN
from src.pathfinding import bfs, getOpenCells

from src.detectorA import detectorTypeA
from src.knowledgeBaseA import initializeKnowledgeBase, updateKnowledgeBase
from src.improvedA import chooseBestPosition, calculateInfoGain

from src.detectorB import runDetectorB, FOUND, PING, NO_PING
from src.knowledgeBaseB import initializeKnowledgeBaseB, updateKnowledgeBaseB
from src.baselineB import chooseBaselineTargetB
from src.improvedB import chooseImprovedTargetB


def calculateDiscoveryCost(moveCount, detectorCount, movementCost=1.0,
                           detectorCost=0.5):
    # this function calculates the total cost of searching for LostBot
    # normally moving costs 1 and using the detector costs 0.5
    # but Q6 makes movement free so we let the costs be changed without
    # rewriting the whole simulation just for that one experiment

    if (
            not math.isfinite(movementCost)
            or not math.isfinite(detectorCost)
            or movementCost < 0
            or detectorCost <= 0
    ):
        raise ValueError("movement cost must be nonnegative and detector cost positive")

    if (
            isinstance(moveCount, bool)
            or isinstance(detectorCount, bool)
            or not isinstance(moveCount, int)
            or not isinstance(detectorCount, int)
            or moveCount < 0
            or detectorCount < 0
    ):
        raise ValueError("action counts must be nonnegative integers")

    totalCost = movementCost * moveCount + detectorCost * detectorCount

    return totalCost


def validateSimulationInputs(grid, locatorPosition, lostBotPosition,
                             detectorType, strategy, k, alpha,
                             movementCost, detectorCost, maxActions):
    # before starting the trial we check whether the ship and parameters
    # are actually valid, because otherwise we might be testing a broken
    # setup instead of the bot's search strategy
    # and then the experiment results would be straight up misleading lol

    if not grid or not all(gridRow for gridRow in grid):
        raise ValueError("ship grid cannot be empty")

    openCells = set(getOpenCells(grid))

    if not openCells:
        raise ValueError("ship needs at least one open cell")

    if locatorPosition not in openCells:
        raise ValueError("LocatorBot must start on an open cell")

    if lostBotPosition not in openCells:
        raise ValueError("LostBot must be placed on an open cell")

    if detectorType not in ("A", "B"):
        raise ValueError("detectorType must be A or B")

    if strategy not in ("baseline", "improved"):
        raise ValueError("strategy must be baseline or improved")

    if detectorType == "A":
        # k is the square detector radius, so negative and fractional
        # values would not describe a valid number of grid cells
        if isinstance(k, bool) or not isinstance(k, int) or k < 0:
            raise ValueError("Type A requires a nonnegative integer k")

    if detectorType == "B":
        # alpha controls how quickly ping probability decreases with
        # Euclidean distance; the detector requires alpha to be positive
        if alpha is None or not math.isfinite(alpha) or alpha <= 0:
            raise ValueError("Type B requires a finite positive alpha")

    calculateDiscoveryCost(0, 0, movementCost, detectorCost)

    if isinstance(maxActions, bool) or not isinstance(maxActions, int) or maxActions < 1:
        raise ValueError("maxActions must be a positive integer")

    # a valid search should be able to reach the LostBot through open cells
    # the generated ships are connected, but manually created test grids
    # might not be, so we check before the simulation starts
    if bfs(grid, locatorPosition, lostBotPosition) is None:
        raise ValueError("LostBot is unreachable from LocatorBot")


def chooseNearestPossibleCell(grid, locatorPosition, possibleCells, rng=None):
    # this is the basic nearest-candidate selection used by Type A baseline
    # and also acts as a fallback if an improved strategy picks a scan
    # position that would leave the bot stuck repeating the same action

    if rng is None:
        rng = random

    shortestDistance = float("inf")
    nearestCells = []

    for cell in possibleCells:
        path = bfs(grid, locatorPosition, cell)

        if path is None:
            continue

        pathDistance = len(path) - 1

        if pathDistance < shortestDistance:
            shortestDistance = pathDistance
            nearestCells = [cell]

        elif pathDistance == shortestDistance:
            nearestCells.append(cell)

    if not nearestCells:
        raise RuntimeError("no reachable possible LostBot locations remain")

    return rng.choice(nearestCells)


def chooseImprovedTargetA(grid, locatorPosition, possibleCells, k,
                          movementCost=1.0, detectorCost=0.5, rng=None):
    # for normal movement cost we use the improved A position selector
    # that my partner wrote, since it balances information gain and travel
    # when movement is free though, distance should NOT affect the score
    # so we compare information gain across all reachable scanning cells

    if rng is None:
        rng = random

    if movementCost > 0:
        # chooseBestPosition uses Python's global random module for ties
        # so we temporarily use our trial RNG state to keep seeded trials
        # reproducible, without permanently changing global random state
        if rng is random:
            return chooseBestPosition(grid, locatorPosition, possibleCells, k)

        savedRandomState = random.getstate()

        try:
            random.setstate(rng.getstate())
            targetPosition = chooseBestPosition(
                grid, locatorPosition, possibleCells, k
            )
            rng.setstate(random.getstate())
        finally:
            random.setstate(savedRandomState)

        return targetPosition

    bestGain = -float("inf")
    bestPositions = []

    for cell in getOpenCells(grid):
        path = bfs(grid, locatorPosition, cell)

        if path is None:
            continue

        informationGain = calculateInfoGain(possibleCells, cell, k)

        if informationGain > bestGain + 1e-12:
            bestGain = informationGain
            bestPositions = [cell]

        elif abs(informationGain - bestGain) <= 1e-12:
            bestPositions.append(cell)

    if not bestPositions:
        raise RuntimeError("no reachable detector positions")

    # with equal information gain, choose a closer position just to
    # keep the movement reasonable even though Q6 doesn't charge for it
    shortestDistance = min(
        len(bfs(grid, locatorPosition, cell)) - 1
        for cell in bestPositions
    )

    closestPositions = [
        cell for cell in bestPositions
        if len(bfs(grid, locatorPosition, cell)) - 1 == shortestDistance
    ]

    return rng.choice(closestPositions)


def chooseSimulationTarget(grid, locatorPosition, knowledgeBase,
                           detectorType, strategy, k=None, alpha=None,
                           movementCost=1.0, detectorCost=0.5, rng=None):
    # all four strategies eventually need to choose a target position
    # this function connects their different interfaces so the main
    # simulation loop doesn't need four separate copies of everything

    if rng is None:
        rng = random

    if detectorType == "A":

        if strategy == "baseline":
            targetPosition = chooseNearestPossibleCell(
                grid, locatorPosition, knowledgeBase, rng
            )

        else:
            targetPosition = chooseImprovedTargetA(
                grid, locatorPosition, knowledgeBase, k,
                movementCost, detectorCost, rng
            )

            # the improved strategy sometimes chooses the cell we're
            # already standing on. if we just detected here, repeating
            # that same deterministic scan tells us nothing new
            if targetPosition is None or targetPosition == locatorPosition:
                targetPosition = chooseNearestPossibleCell(
                    grid, locatorPosition, knowledgeBase, rng
                )

    else:

        if strategy == "baseline":
            targetPosition = chooseBaselineTargetB(
                grid, locatorPosition, knowledgeBase, rng
            )

        else:
            targetPosition = chooseImprovedTargetB(
                grid, locatorPosition, knowledgeBase, alpha,
                movementCost=movementCost,
                detectorCost=detectorCost,
                rng=rng
            )

            # repeated Type B readings can provide new evidence because
            # the detector is probabilistic, unlike Type A
            # but we avoid staying forever by moving toward the strongest
            # remaining candidate if the selected target is our current cell
            if targetPosition == locatorPosition:
                targetPosition = chooseBaselineTargetB(
                    grid, locatorPosition, knowledgeBase, rng
                )

    return targetPosition


def getSimulationPath(grid, locatorPosition, targetPosition):
    # BFS gives the shortest legal route through open cells
    # we check it before moving so the bot cannot teleport through walls
    # or somehow leave the ship. absolutely not happening

    if targetPosition is None:
        raise RuntimeError("strategy did not choose a target")

    path = bfs(grid, locatorPosition, targetPosition)

    if path is None:
        raise RuntimeError("strategy chose an unreachable target")

    if not path or path[0] != locatorPosition or path[-1] != targetPosition:
        raise RuntimeError("BFS returned an invalid movement path")

    for nextPosition in path:
        if grid[nextPosition[0]][nextPosition[1]] != OPEN:
            raise RuntimeError("movement path contains a blocked cell")

    return path


def runSimulation(grid, locatorPosition, lostBotPosition,
                  detectorType, strategy, k=None, alpha=None,
                  movementCost=1.0, detectorCost=0.5,
                  maxActions=100000, rng=None):
    # this function runs one complete search trial from start to finish
    # the LostBot stays in one cell while LocatorBot keeps detecting,
    # updating its knowledge, and choosing where to move next
    #
    # the main goal is to count EVERY action accurately so the baseline
    # and improved strategies can be compared using the same rules

    validateSimulationInputs(
        grid, locatorPosition, lostBotPosition,
        detectorType, strategy, k, alpha,
        movementCost, detectorCost, maxActions
    )

    if rng is None:
        rng = random.Random()

    startingPosition = locatorPosition

    moveCount = 0
    detectorCount = 0
    detectorHistory = []
    positionHistory = [locatorPosition]

    # initialize the prior BEFORE the first detector reading
    # including the starting cell is important because FOUND is possible
    # if the bots happen to start in the same position
    if detectorType == "A":
        knowledgeBase = initializeKnowledgeBase(grid)
    else:
        knowledgeBase = initializeKnowledgeBaseB(grid)

    while True:

        if moveCount + detectorCount >= maxActions:
            raise RuntimeError("simulation exceeded the maximum number of actions")

        # run the detector at the LocatorBot's current position
        # Type A gives a deterministic ping/no ping based on the square
        # Type B gives a probabilistic ping based on Euclidean distance
        if detectorType == "A":
            detectorResult = detectorTypeA(
                locatorPosition, lostBotPosition, k
            )
        else:
            detectorResult = runDetectorB(
                locatorPosition, lostBotPosition, alpha, rng
            )

        detectorCount += 1
        detectorHistory.append(detectorResult)

        # FOUND is terminal for both detectors, so we stop immediately
        # and do not charge for an extra move or detector reading
        if detectorResult.lower() == "found":
            break

        # after each observation, remove or reweight impossible locations
        # Type A keeps a set; Type B keeps a Bayesian probability dictionary
        if detectorType == "A":
            knowledgeBase = updateKnowledgeBase(
                knowledgeBase, locatorPosition, k, detectorResult
            )

            if not knowledgeBase:
                raise RuntimeError("Type A knowledge base has no possible locations")

        else:
            knowledgeBase = updateKnowledgeBaseB(
                knowledgeBase, locatorPosition, detectorResult, alpha
            )

        # choose where the strategy wants the bot to go next
        targetPosition = chooseSimulationTarget(
            grid, locatorPosition, knowledgeBase,
            detectorType, strategy, k, alpha,
            movementCost, detectorCost, rng
        )

        path = getSimulationPath(grid, locatorPosition, targetPosition)

        if len(path) < 2:
            raise RuntimeError("strategy made no movement progress")

        if movementCost == 0:
            # Q6: movement is free, so travel along the WHOLE BFS path
            # to the selected detector position before taking another scan
            # the physical moves still get counted, just not charged
            nextPositions = path[1:]
        else:
            # normal assignment: one adjacent movement action at a time
            # then detect again using the newly reached position
            nextPositions = path[1:2]

        for nextPosition in nextPositions:

            if moveCount + detectorCount >= maxActions:
                raise RuntimeError("simulation exceeded the maximum number of actions")

            locatorPosition = nextPosition
            positionHistory.append(locatorPosition)
            moveCount += 1

    totalCost = calculateDiscoveryCost(
        moveCount, detectorCount, movementCost, detectorCost
    )

    # return one consistent results dictionary for every strategy
    # experiments.py can collect these without worrying about A/B
    # using completely different names for their action counts
    return {
        "detector_type": detectorType,
        "strategy": strategy,
        "start_position": startingPosition,
        "lost_bot_position": lostBotPosition,
        "final_position": locatorPosition,
        "moves": moveCount,
        "detector_actions": detectorCount,
        "total_cost": totalCost,
        "found": True,
        "movement_cost": movementCost,
        "detector_cost": detectorCost,
        "detector_history": detectorHistory,
        "position_history": positionHistory,
        "final_knowledge_base": knowledgeBase
    }


def runAllStrategies(grid, locatorPosition, lostBotPosition,
                     k, alpha, movementCost=1.0,
                     detectorCost=0.5, maxActions=100000,
                     seed=None):
    # this runs all four search strategies on the SAME ship and same
    # starting/hidden bot positions, which is useful for fair comparisons
    # the random detector outcomes can still vary between strategies,
    # so experiments.py should repeat many trials before drawing conclusions

    strategyConfigs = [
        ("A", "baseline"),
        ("A", "improved"),
        ("B", "baseline"),
        ("B", "improved")
    ]

    allResults = {}

    for detectorType, strategy in strategyConfigs:

        # separate random generators mean one strategy does not consume
        # another strategy's random choices during the comparison
        trialRng = random.Random(seed) if seed is not None else random.Random()

        trialResult = runSimulation(
            grid=grid,
            locatorPosition=locatorPosition,
            lostBotPosition=lostBotPosition,
            detectorType=detectorType,
            strategy=strategy,
            k=k,
            alpha=alpha,
            movementCost=movementCost,
            detectorCost=detectorCost,
            maxActions=maxActions,
            rng=trialRng
        )

        allResults[f"{detectorType}_{strategy}"] = trialResult

    return allResults
