import time

from src.initial import random_initial_state
from src.objective import objective
from src.neighbors import get_all_neighbors


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