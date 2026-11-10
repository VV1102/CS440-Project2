import csv
import random
from pathlib import Path
from statistics import mean

from src.pathfinding import getOpenCells
from src.ship import generate_ship
from src.simulation import runSimulation


# These are tentative settings for the experiments
SHIP_SIZES = [20]
SHIPS_PER_SIZE = 2
TRIALS_PER_SHIP = 10
TYPE_A_K_VALUES = []
TYPE_B_ALPHA_VALUES = [0.25, 0.5, 1.0, 1.5]
MAX_ACTIONS = 3000
MOVEMENT_COST = 0.0
DETECTOR_COST = 0.5
SEED = 440

# makes sure we save the results in the project folder
OUTPUT_FOLDER = Path(__file__).resolve().parent


def createShip(size, seed):
    # generates a ship using the same seed so results can be repeated
    oldState = random.getstate()

    try: #this part makes sure the random generator is reset to the previous state after ship generation
        random.seed(seed)
        return generate_ship(size)
    finally:
        random.setstate(oldState)


#this function runs a pair of trials each for baseline and improved, with same ship and starting positions
def runPair(grid, startPosition, lostBotPosition, detectorType, parameter, seed):
    # we run baseline and improved on the same ship
    results = {}

    for strategy in ("baseline", "improved"):
        print(
            f"Running Type {detectorType}, " #printing the strategy, detector type and parameter
            f"Strategy: {strategy}, "
            f"Parameter: {parameter}"
        )

        # use a separate random generator for each strategy
        trialRng = random.Random(seed)

        try: #this part runs the simulation for the given strategy and saves the results
            results[strategy] = runSimulation(
                grid=grid,
                locatorPosition=startPosition,
                lostBotPosition=lostBotPosition,
                detectorType=detectorType,
                strategy=strategy,
                k=parameter if detectorType == "A" else None,
                alpha=parameter if detectorType == "B" else None,
                movementCost=MOVEMENT_COST,
                detectorCost=DETECTOR_COST,
                maxActions=MAX_ACTIONS,
                rng=trialRng
            )

        except (ValueError, RuntimeError) as error:
            # this saves which strategy failed
            print(f"{strategy} failed: {error}")
            results[strategy] = None

    return results


# this function saves the results of the experiments into CSV files
def saveCsv(filename, rows, columns):
    # saves the experiment results into a CSV file
    with (OUTPUT_FOLDER / filename).open(
        "w", newline="", encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

# this function runs the experiments for different ship sizes, detector types, and parameters
def runExperiments():
    # stores individual results, averages, and failed trials
    trialRows = []
    summaryRows = []
    failureRows = []

    # we test different ship sizes
    for size in SHIP_SIZES:

        # Generate multiple ships for each size
        for shipNumber in range(SHIPS_PER_SIZE):

            shipSeed = SEED + size * 1000 + shipNumber

            grid = createShip(size, shipSeed)
            openCells = getOpenCells(grid)

            # we make sure the ship has enough open cells
            if len(openCells) < 2:
                raise ValueError("Ship must have at least two open cells")

            # Choose starting and LostBot positions
            scenarioRng = random.Random(shipSeed + 500000)

            scenarios = [
                scenarioRng.sample(openCells, 2)
                for _ in range(TRIALS_PER_SHIP)
            ]

            # we run experiments for Type A and Type B
            for detectorType, parameters in (
                ("A", TYPE_A_K_VALUES),
                ("B", TYPE_B_ALPHA_VALUES)
            ):

                for parameter in parameters:
                    pairedResults = []
                    failed = 0

                    # we run each trial using the same positions
                    for trialNumber, (start, lostBot) in enumerate(
                        scenarios, 1
                    ):

                        trialSeed = shipSeed * 100 + trialNumber
                        # we run a pair of trials for baseline and improved strategies
                        try:
                            pair = runPair(
                                grid,
                                start,
                                lostBot,
                                detectorType,
                                parameter,
                                trialSeed
                            )

                        except (ValueError, RuntimeError) as error:
                            failed += 1

                            failureRows.append({
                                "ship_size": size,
                                "ship_number": shipNumber + 1,
                                "detector_type": detectorType,
                                "parameter": parameter,
                                "trial": trialNumber,
                                "error": str(error)
                            })

                            print(
                                f"FAILED: Type {detectorType}, "
                                f"size={size}, "
                                f"ship={shipNumber + 1}, "
                                f"parameter={parameter}, "
                                f"trial={trialNumber}: {error}"
                            )

                            continue

                        baseline = pair["baseline"]
                        improved = pair["improved"]
                        # this part skips paired cost comparison if either strategy failed
                        if baseline is None or improved is None:
                            failed += 1
                            failureRows.append({
                                "ship_size": size,
                                "ship_number": shipNumber + 1,
                                "detector_type": detectorType,
                                "parameter": parameter,
                                "trial": trialNumber,
                                "error": "One or both strategies exceeded the action limit"
                            })
                            continue

                        pairedResults.append(pair)

                        # makes sure to save the results of each trial
                        trialRows.append({
                            "ship_size": size,
                            "ship_number": shipNumber + 1,
                            "detector_type": detectorType,
                            "parameter": parameter,
                            "trial": trialNumber,
                            "start_position": str(start),
                            "lost_bot_position": str(lostBot),
                            "baseline_moves": baseline["moves"],
                            "improved_moves": improved["moves"],
                            "baseline_scans": baseline["detector_actions"],
                            "improved_scans": improved["detector_actions"],
                            "baseline_cost": baseline["total_cost"],
                            "improved_cost": improved["total_cost"]
                        })

                    completed = len(pairedResults)

                    # skip averages if no trials were completed
                    if not completed:
                        print(
                            f"No completed pairs for Type {detectorType}, "
                            f"size={size}, ship={shipNumber + 1}, "
                            f"parameter={parameter}"
                        )
                        continue

                    # calculate average costs
                    baselineCosts = [
                        x["baseline"]["total_cost"]
                        for x in pairedResults
                    ]

                    improvedCosts = [
                        x["improved"]["total_cost"]
                        for x in pairedResults
                    ]

                    avgBaseline = mean(baselineCosts)
                    avgImproved = mean(improvedCosts)

                    # we calculate the percentage improvement
                    improvement = (
                        100 * (avgBaseline - avgImproved) / avgBaseline
                    )

                    # we store the average results
                    summaryRows.append({
                        "ship_size": size,
                        "ship_number": shipNumber + 1,
                        "detector_type": detectorType,
                        "parameter": parameter,
                        "completed_trials": completed,
                        "failed_trials": failed,

                        "baseline_avg_moves": round(
                            mean(x["baseline"]["moves"]
                                 for x in pairedResults), 2
                        ),
                        # we calculate the average moves for the improved strategy
                        "improved_avg_moves": round(
                            mean(x["improved"]["moves"]
                                 for x in pairedResults), 2
                        ),
                        # we calculate the average scans for the baseline strategy
                        "baseline_avg_scans": round(
                            mean(x["baseline"]["detector_actions"]
                                 for x in pairedResults), 2
                        ),
                        # we calculate the average scans for the improved strategy
                        "improved_avg_scans": round(
                            mean(x["improved"]["detector_actions"]
                                 for x in pairedResults), 2
                        ),
                        # we calculate the average cost for the baseline strategy
                        "baseline_avg_cost": round(avgBaseline, 2),
                        "improved_avg_cost": round(avgImproved, 2),
                        "improvement_percent": round(improvement, 2)
                    })

                    # we prints the results in the terminal
                    label = "k" if detectorType == "A" else "alpha"

                    print(
                        f"Type {detectorType} | {size}x{size} | "
                        f"ship {shipNumber + 1} | "
                        f"{label}={parameter} | "
                        f"{completed}/{TRIALS_PER_SHIP} pairs"
                    )

                    print(
                        f"  Baseline: {avgBaseline:.2f} "
                        f"Improved: {avgImproved:.2f} "
                        f"Change: {improvement:+.2f}%"
                    )

    # Column names for the CSV files
    trialColumns = [
        "ship_size", "ship_number", "detector_type", "parameter",
        "trial", "start_position", "lost_bot_position",
        "baseline_moves", "improved_moves",
        "baseline_scans", "improved_scans",
        "baseline_cost", "improved_cost"
    ]
    # these are the column names for the summary CSV file
    summaryColumns = [
        "ship_size", "ship_number", "detector_type", "parameter",
        "completed_trials", "failed_trials",
        "baseline_avg_moves", "improved_avg_moves",
        "baseline_avg_scans", "improved_avg_scans",
        "baseline_avg_cost", "improved_avg_cost",
        "improvement_percent"
    ]

    failureColumns = [
        "ship_size", "ship_number", "detector_type",
        "parameter", "trial", "error"
    ]

    # we save all the results
    saveCsv("../report/results_comparison/experiment_trials.csv", trialRows, trialColumns)
    saveCsv("../report/results_comparison/experiment_summary.csv", summaryRows, summaryColumns)
    saveCsv("../report/results_comparison/experiment_failures.csv", failureRows, failureColumns)

    print(
        "\nSaved experiment_trials.csv, "
        "experiment_summary.csv, and experiment_failures.csv"
    )
    # we print a warning if there were any failed trials
    if failureRows:
        print(
            f"WARNING: {len(failureRows)} pairs failed. "
            "Check experiment_failures.csv before using the averages."
        )
    else:
        print("All experiment pairs completed successfully.")


if __name__ == "__main__":
    runExperiments()

