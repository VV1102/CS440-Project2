
# Project 2: Where Is It?

## Summary

In this project, we are simulating the process of the LocatorBot locating the lost LostBot in a randomly generated spaceship
LocatorBot uses the detectors to collect information and update its knowledge about LostBot’s location
Two types of detectors were used to implement both basic and improved approaches to the search problem

---

## Ship Generation and Pathfinding

Ship: The ship consists of randomly generated 'D x D' matrix consisting of OPEN and BLOCKED cells
Both LocatorBot and LostBot begin in different open cells
Shortest path is found using BFS (Breadth First Search) algorithm to find paths between two cells without hitting any wall

---

## Type A Detector

Type A is a deterministic sensor with a square sensing area that can be set by parameter `k`
It gives FOUND, PING, or NO PING
The knowledge base holds all possible LostBot positions and eliminates conflicting cells after each sensing step

### Baseline A

Uses BFS to head towards the nearest position of the LostBot

### Improved A

Uses binary entropy for estimating information gain and balances with movement and detector costs

`score = information_gain / (BFS_distance + 0.5)`

So the locatorbot chooses the scan position with the highest score
In case the scans cannot narrow down the location possibilities, then it reverts to the closest possible location cell
---

## Type B Detector

Now Type B is probabilistic and its ping probability depends on distance and `alpha`
`P(ping) = e^(-alpha * (distance - 1))`

This knowledge database contains the probabilities associated with each potential LostBot position and revises them according to Bayes' theorem

### Baseline B

Choses the cell that is most likely to have LostBot in it, breaking ties with the BFS distance
### Improved B

This takes in info expected information gain, discovery probability, and movement cost
formula
`score = (expected_information_gain + discovery_probability) / (BFS_distance + 0.5)`

Thus, The bot chooses the place with the greatest score and updates its information after each scan.
---

## Simulation

This simulation consists of ship generation, detectors, pathfinding, and search algorithms.

In each iteration:

1. LocatorBot picks a target
2. Travels to the target via BFS
3. Runs the detector
4. Updates the knowledge database
5. And so on, until it locates the LostBot

The simulation measures the number of moves, scans, and total discovery costs.

---

## Experiments

The comparison between the baseline and the improved algorithms is done for different settings of the detector:

- **Type A:** Different values for `k`.
- **Type B:** Different values for `alpha`.
- **No movement:** Cost of movement is zero.

DiscoveryCost calculation is:

`total_cost = (moves * movement_cost) + (scans * detector_cost)`

Normal costs:
- Movement: `1`
- Detector: `0.5`

The experiment outcomes are saved as CSV files for the purpose of comparing the averages discovery costs.

---

## Project Structure

| File | Purpose |
|------|---------|
| `src/ship.py` | Generates ship layouts |
| `src/pathfinding.py` | BFS and pathfinding |
| `src/detectorA.py`, `src/detectorB.py` | Detector behavior |
| `src/knowledgeBaseA.py`, `src/knowledgeBaseB.py` | Knowledge base updates |
| `src/baselineA.py`, `src/baselineB.py` | Baseline strategies |
| `src/improvedA.py`, `src/improvedB.py` | Improved strategies |
| `src/simulation.py` | Runs simulations and tracks costs |
| `src/experiments.py` | Runs trials and exports results |
| `tests/` | Automated tests |

---

## Running the Tests

From the project folder:

```bash
python -m pytest -v
```

---

## Running the Experiments

```bash
python -m src.experiments
```

Experiment settings can be changed in `src/experiments.py`.

The script generates:
- `experiment_trials.csv`
- `experiment_summary.csv`
- `experiment_failures.csv`

---

## Main Goal

We will explore if using information gain and probabilities in favor of selecting the closest or most probable location will allow LocatorBot to locate LostBot with more efficiency.

Experiments will allow us to evaluate when the improved approaches are advantageous and when the baseline methods are superior.
