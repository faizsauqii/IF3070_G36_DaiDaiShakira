import time

from src.initial import random_initial_state
from src.objective import objective
from src.neighbors import get_all_neighbors, get_random_neighbor


def hill_climb(problem, rng, initial_state=None):
    start_time = time.perf_counter()
    used_fallback = False
    if initial_state is None:
        initial_state, used_fallback = random_initial_state(problem, rng)

    current = initial_state
    current_value = objective(current)
    history = [current_value]
    moves = []

    while True:
        best_move, best_state, best_value = None, None, current_value
        for move, neighbor in get_all_neighbors(current):
            value = objective(neighbor)
            if value > best_value:
                best_move, best_state, best_value = move, neighbor, value
        if best_state is None:
            break
        current, current_value = best_state, best_value
        history.append(current_value)
        moves.append(best_move)

    return {
        "algorithm": "hc",
        "initial_state": initial_state,
        "final_state": current,
        "history": history,
        "moves": moves,
        "iterations": len(moves),
        "duration_s": time.perf_counter() - start_time,
        "used_fallback": used_fallback,
    }


def hill_climb_sideways(problem, rng, initial_state=None, max_sideways=100):
    start_time = time.perf_counter()
    used_fallback = False
    if initial_state is None:
        initial_state, used_fallback = random_initial_state(problem, rng)

    current = initial_state
    current_value = objective(current)
    history = [current_value]
    moves = []
    sideways = 0

    while True:
        best_value = None
        best = []
        for move, neighbor in get_all_neighbors(current):
            value = objective(neighbor)
            if best_value is None or value > best_value:
                best_value, best = value, [(move, neighbor)]
            elif value == best_value:
                best.append((move, neighbor))
        if best_value is None or best_value < current_value:
            break
        if best_value == current_value:
            if sideways >= max_sideways:
                break
            sideways += 1
        move, current = rng.choice(best)
        current_value = best_value
        history.append(current_value)
        moves.append(move)

    return {
        "algorithm": "hc_sideways",
        "params": {"max_sideways": max_sideways},
        "initial_state": initial_state,
        "final_state": current,
        "history": history,
        "moves": moves,
        "iterations": len(moves),
        "sideways_moves": sideways,
        "duration_s": time.perf_counter() - start_time,
        "used_fallback": used_fallback,
    }


def hill_climb_stochastic(problem, rng, initial_state=None, max_iterations=1000):
    start_time = time.perf_counter()
    used_fallback = False
    if initial_state is None:
        initial_state, used_fallback = random_initial_state(problem, rng)

    current = initial_state
    current_value = objective(current)
    history = [current_value]
    moves = []
    invalid = 0

    for _ in range(max_iterations):
        move, neighbor = get_random_neighbor(current, rng)
        if neighbor is None:
            invalid += 1
        else:
            value = objective(neighbor)
            if value > current_value:
                current, current_value = neighbor, value
                moves.append(move)
        history.append(current_value)

    return {
        "algorithm": "hc_stochastic",
        "params": {"max_iterations": max_iterations},
        "initial_state": initial_state,
        "final_state": current,
        "history": history,
        "moves": moves,
        "iterations": max_iterations,
        "invalid_neighbors": invalid,
        "duration_s": time.perf_counter() - start_time,
        "used_fallback": used_fallback,
    }


def hill_climb_random_restart(problem, rng, initial_state=None, max_restarts=10):
    start_time = time.perf_counter()
    first = hill_climb(problem, rng, initial_state)
    best = first
    history = list(first["history"])
    iterations_per_restart = [first["iterations"]]
    used_fallback = first["used_fallback"]

    for _ in range(max_restarts):
        result = hill_climb(problem, rng)
        history += result["history"]
        iterations_per_restart.append(result["iterations"])
        used_fallback = used_fallback or result["used_fallback"]
        if result["history"][-1] > best["history"][-1]:
            best = result

    return {
        "algorithm": "hc_random_restart",
        "params": {"max_restarts": max_restarts},
        "initial_state": first["initial_state"],
        "final_state": best["final_state"],
        "history": history,
        "moves": best["moves"],
        "iterations": sum(iterations_per_restart),
        "restarts": max_restarts,
        "iterations_per_restart": iterations_per_restart,
        "duration_s": time.perf_counter() - start_time,
        "used_fallback": used_fallback,
    }