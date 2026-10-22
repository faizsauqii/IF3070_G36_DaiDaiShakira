import argparse
import json
import os
import random
import argparse
import json
import os
import random
import sys

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
from src.algorithms.ga import genetic_algorithm
from src.visual import plot_objective_history, plot_deck_state

ALGORITHMS = {
    "hc": hill_climb,
    "hc_sideways": hill_climb_sideways,
    "hc_stochastic": hill_climb_stochastic,
    "hc_random_restart": hill_climb_random_restart,
    "sa": simulated_annealing,
    "ga": genetic_algorithm,
}


NAMES = {
    "hc": "Steepest Ascent Hill-Climbing",
    "hc_sideways": "Hill-Climbing with Sideways Move",
    "hc_stochastic": "Stochastic Hill-Climbing",
    "hc_random_restart": "Random Restart Hill-Climbing",
    "sa": "Simulated Annealing",
    "ga": "Genetic Algorithm",
}


CORE_KEYS = {
    "algorithm", "params", "initial_state", "final_state", "best_state",
    "history", "moves", "iterations", "duration_s", "used_fallback",
}


def state_to_list(state):
    result = []
    for vehicle, pos, orientation in zip(state.problem.vehicles, state.positions, state.orientations):
        ship, x, y = pos if pos is not None else (None, None, None)
        result.append({"id": vehicle.id, "ship": ship, "x": x, "y": y, "orientation": orientation})
    return result


def build_record(problem, result, data_file, seed, params):
    final_state = result["final_state"]
    extra = {key: value for key, value in result.items() if key not in CORE_KEYS}
    extra["moves"] = [describe_move(problem, m) for m in result.get("moves", [])]
    record = {
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
    best_state = result.get("best_state")
    if best_state is not None:
        record["best_state"] = state_to_list(best_state)
        record["best_fee"] = total_fee(best_state)
        record["best_objective"] = objective(best_state)
    return record


def save_record(record, run):
    folder = os.path.join("output", record["algorithm"])
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"run{run}_seed{record['seed']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    return path


def save_plots(result, record, run):
    base = os.path.join("output", record["algorithm"], f"run{run}_seed{record['seed']}")
    plot_objective_history(result, f"{base}_objective.png")
    plot_deck_state(result["initial_state"], f"{base}_awal.png", title="State Awal")
    plot_deck_state(result["final_state"], f"{base}_akhir.png", title="State Akhir")


def run_experiment(algorithm, data_file, seeds):
    problem = load_problem(data_file)
    run_algorithm = ALGORITHMS[algorithm]
    records = []
    for run, seed in enumerate(seeds, start=1):
        result = run_algorithm(problem, random.Random(seed))
        record = build_record(problem, result, data_file, seed, {})
        path = save_record(record, run)
        save_plots(result, record, run)
        print(f"run {run} seed {seed}: fee {record['final_fee']}, iterasi {record['iterations']}, {record['duration_s']:.3f} s -> {path}")
        records.append(record)
    return records


def ask_number(prompt, low, high, default=None):
    while True:
        text = input(prompt).strip()
        if text == "" and default is not None:
            return default
        if text.isdigit() and low <= int(text) <= high:
            return int(text)
        print("Pilihan tidak valid, coba lagi.")


def choose_from(title, options, zero_label):
    print(f"\n{title}")
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")
    print(f"  0. {zero_label}")
    return ask_number("Pilih nomor: ", 0, len(options))


def show_result(records):
    best_run, best = max(enumerate(records, start=1), key=lambda item: item[1]["final_fee"])
    print(f"\nHasil terbaik: run {best_run} (seed {best['seed']}), fee {best['final_fee']}")
    print("Kendaraan yang dimuat:")
    for v in best["final_state"]:
        if v["ship"] is not None:
            print(f"  {v['id']} -> kapal {v['ship'] + 1}, posisi ({v['x']}, {v['y']}), {v['orientation']}")
    waiting = [v["id"] for v in best["final_state"] if v["ship"] is None]
    print("Tidak dimuat: " + (", ".join(waiting) if waiting else "-"))


def menu():
    algorithms = list(ALGORITHMS)
    data_files = sorted(f for f in os.listdir("data") if f.endswith(".json"))
    while True:
        names = [NAMES.get(key, key) for key in algorithms]
        pick = choose_from("=== Menu Utama: pilih algoritma ===", names, "Keluar")
        if pick == 0:
            print("Sampai jumpa!")
            return
        data_pick = choose_from("Pilih file data:", data_files, "Kembali")
        if data_pick == 0:
            continue
        runs = ask_number("Mau dijalankan berapa kali? (Enter = 1): ", 1, 10, default=1)
        data_file = os.path.join("data", data_files[data_pick - 1])
        records = run_experiment(algorithms[pick - 1], data_file, list(range(1, runs + 1)))
        show_result(records)


def main():
    if len(sys.argv) == 1:
        try:
            menu()
        except (KeyboardInterrupt, EOFError):
            print("\nProgram dihentikan.")
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("--algorithm", choices=list(ALGORITHMS), default="hc")
    parser.add_argument("--data", default="data/kecil.json")
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    run_experiment(args.algorithm, args.data, args.seeds)


if __name__ == "__main__":
    main()
