import argparse
import json
import os
import random
import time

from src.constraints import is_valid
from src.initial import random_initial_state
from src.loader import load_problem
from src.models import State
from src.neighbors import get_random_neighbor
from src.objective import objective, total_fee


def make_population(problem, size, rng, p):
    population = []
    used_fallback = False
    for _ in range(size):
        state, fallback = random_initial_state(problem, rng, p)
        population.append(state)
        used_fallback = used_fallback or fallback
    return population, used_fallback


def roulette(population, scores, rng):
    total = sum(scores)
    if total <= 0:
        return rng.choice(population)
    target = rng.uniform(0, total)
    acc = 0.0
    for individual, score in zip(population, scores):
        acc += score
        if acc >= target:
            return individual
    return population[-1]


def crossover(a, b, rng):
    child = State.empty(a.problem)
    order = list(range(len(a.problem.vehicles)))
    rng.shuffle(order)
    for i in order:
        parents = [a, b] if rng.random() < 0.5 else [b, a]
        for parent in parents:
            if not parent.is_inside(i):
                continue
            child.positions[i] = parent.positions[i]
            child.orientations[i] = parent.orientations[i]
            if is_valid(child):
                break
            child.positions[i] = None
            child.orientations[i] = None
    return child


def mutate(state, rate, rng):
    if rng.random() >= rate:
        return state
    _, neighbor = get_random_neighbor(state, rng)
    return neighbor if neighbor is not None else state


def best_index(scores):
    return max(range(len(scores)), key=scores.__getitem__)


def genetic_algorithm(
    problem,
    rng,
    population_size=50,
    iterations=100,
    p=0.3,
    crossover_rate=0.9,
    mutation_rate=0.3,
    elite=1,
):
    start_time = time.perf_counter()

    population, used_fallback = make_population(problem, population_size, rng, p)
    scores = [objective(s) for s in population]

    initial_state = population[best_index(scores)]
    history = [max(scores)]
    history_avg = [sum(scores) / population_size]

    for _ in range(iterations):
        ranked = sorted(range(population_size), key=scores.__getitem__, reverse=True)
        next_population = [population[k] for k in ranked[:elite]]
        next_scores = [scores[k] for k in ranked[:elite]]
        while len(next_population) < population_size:
            a = roulette(population, scores, rng)
            b = roulette(population, scores, rng)
            if rng.random() < crossover_rate:
                child = crossover(a, b, rng)
            else:
                child = a.copy()
            child = mutate(child, mutation_rate, rng)
            next_population.append(child)
            next_scores.append(objective(child))
        population, scores = next_population, next_scores
        history.append(max(scores))
        history_avg.append(sum(scores) / population_size)

    return {
        "algorithm": "ga",
        "initial_state": initial_state,
        "final_state": population[best_index(scores)],
        "history": history,
        "history_avg": history_avg,
        "population_size": population_size,
        "iterations": iterations,
        "duration_s": time.perf_counter() - start_time,
        "used_fallback": used_fallback,
    }


def state_to_list(state):
    result = []
    for vehicle, pos, orientation in zip(state.problem.vehicles, state.positions, state.orientations):
        ship, x, y = pos if pos is not None else (None, None, None)
        result.append({"id": vehicle.id, "ship": ship, "x": x, "y": y, "orientation": orientation})
    return result


def build_record(result, data_file, seed, params):
    final_state = result["final_state"]
    return {
        "algorithm": result["algorithm"],
        "data_file": data_file,
        "seed": seed,
        "params": params,
        "initial_state": state_to_list(result["initial_state"]),
        "final_state": state_to_list(final_state),
        "initial_fee": total_fee(result["initial_state"]),
        "final_fee": total_fee(final_state),
        "final_objective": objective(final_state),
        "iterations": result["iterations"],
        "duration_s": result["duration_s"],
        "used_fallback": result["used_fallback"],
        "history": result["history"],
        "extra": {
            "population_size": result["population_size"],
            "history_avg": result["history_avg"],
        },
    }


def experiment_configs(control_population, iteration_variants, control_iterations, population_variants):
    configs = [("kontrol_populasi", control_population, it) for it in iteration_variants]
    configs += [("kontrol_iterasi", pop, control_iterations) for pop in population_variants]
    return configs


def run_experiments(
    data_file,
    control_population,
    iteration_variants,
    control_iterations,
    population_variants,
    seeds,
    output_dir="output",
    **ga_params,
):
    problem = load_problem(data_file)
    dataset = os.path.splitext(os.path.basename(data_file))[0]
    summary = []
    configs = experiment_configs(control_population, iteration_variants, control_iterations, population_variants)
    for group, population_size, iterations in configs:
        folder = os.path.join(output_dir, "ga", dataset, group)
        os.makedirs(folder, exist_ok=True)
        for run, seed in enumerate(seeds, start=1):
            params = {"population_size": population_size, "iterations": iterations, **ga_params}
            result = genetic_algorithm(problem, random.Random(seed), **params)
            record = build_record(result, data_file, seed, params)
            path = os.path.join(folder, f"pop{population_size}_iter{iterations}_run{run}_seed{seed}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)
            row = {
                "group": group,
                "population_size": population_size,
                "iterations": iterations,
                "run": run,
                "seed": seed,
                "initial_fee": record["initial_fee"],
                "final_fee": record["final_fee"],
                "duration_s": record["duration_s"],
                "path": path,
            }
            summary.append(row)
            print(
                f"{group:<17} pop {population_size:>4} iter {iterations:>4} run {run} seed {seed}: "
                f"fee {row['initial_fee']} -> {row['final_fee']}, {row['duration_s']:.2f} s"
            )
    with open(os.path.join(output_dir, "ga", dataset, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/kecil.json")
    parser.add_argument("--control-population", type=int, default=50)
    parser.add_argument("--iteration-variants", type=int, nargs=3, default=[50, 100, 200])
    parser.add_argument("--control-iterations", type=int, default=100)
    parser.add_argument("--population-variants", type=int, nargs=3, default=[20, 50, 100])
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--p", type=float, default=0.3)
    parser.add_argument("--crossover-rate", type=float, default=0.9)
    parser.add_argument("--mutation-rate", type=float, default=0.3)
    parser.add_argument("--elite", type=int, default=1)
    args = parser.parse_args()

    run_experiments(
        args.data,
        args.control_population,
        args.iteration_variants,
        args.control_iterations,
        args.population_variants,
        args.seeds,
        p=args.p,
        crossover_rate=args.crossover_rate,
        mutation_rate=args.mutation_rate,
        elite=args.elite,
    )


if __name__ == "__main__":
    main()
