import argparse
import json
import os
import random

from src.loader import load_problem
from src.objective import total_fee, objective
from src.neighbors import describe_move
from src.algorithms.hc import (
    hill_climb,
    hill_climb_sideways,
    hill_climb_stochastic,
    hill_climb_random_restart,
)
from src.algorithms.sa import simulated_annealing

ALGORITHMS = {
    "hc": hill_climb,
    "hc_sideways": hill_climb_sideways,
    "hc_stochastic": hill_climb_stochastic,
    "hc_random_restart": hill_climb_random_restart,
    "sa": simulated_annealing,
}

EXTRA_KEYS = ["sideways_moves", "invalid_neighbors", "restarts", "iterations_per_restart"]


def state_to_list(state):
    result = []
    for vehicle, pos, orientation in zip(state.problem.vehicles, state.positions, state.orientations):
        ship, x, y = pos if pos is not None else (None, None, None)
        result.append({"id": vehicle.id, "ship": ship, "x": x, "y": y, "orientation": orientation})
    return result


def build_record(problem, result, data_file, seed, params):
    final_state = result["final_state"]
    extra = {key: result[key] for key in EXTRA_KEYS if key in result}
    extra["moves"] = [describe_move(problem, m) for m in result.get("moves", [])]
    return {
        "algorithm": result["algorithm"],
        "data_file": data_file,
        "seed": seed,
        "params": result.get("params", params),
        "initial_state": state_to_list(result["initial_state"]),
        "final_state": state_to_list(final_state),
        "final_fee": total_fee(final_state),
        "final_objective": objective(final_state),
        "iterations": result["iterations"],
        "duration_s": result["duration_s"],
        "used_fallback": result["used_fallback"],
        "history": result["history"],
        "extra": extra,
    }


def save_record(record, run):
    folder = os.path.join("output", record["algorithm"])
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"run{run}_seed{record['seed']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algorithm", choices=list(ALGORITHMS), default="hc")
    parser.add_argument("--data", default="data/kecil.json")
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()

    problem = load_problem(args.data)
    run_algorithm = ALGORITHMS[args.algorithm]
    for run, seed in enumerate(args.seeds, start=1):
        result = run_algorithm(problem, random.Random(seed))
        record = build_record(problem, result, args.data, seed, {})
        path = save_record(record, run)
        print(f"run {run} seed {seed}: fee {record['final_fee']}, iterasi {record['iterations']}, {record['duration_s']:.3f} s -> {path}")


if __name__ == "__main__":
    main()
