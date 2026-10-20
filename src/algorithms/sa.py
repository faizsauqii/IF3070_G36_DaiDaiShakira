"""Simulated Annealing untuk masalah penempatan kendaraan.
"""

import time

from src.initial import random_initial_state
from src.objective import objective


def simulated_annealing(
    problem,
    rng,
    initial_state=None,
    initial_temp=60.0,
    cooling_rate=0.995,
    max_iterations=1000,
):
    """Persiapan state awal dan struktur hasil untuk pencarian SA."""

    if initial_temp <= 0:
        raise ValueError("initial_temp harus lebih dari 0")

    if not 0 < cooling_rate < 1:
        raise ValueError("cooling_rate harus di antara 0 dan 1")

    if not isinstance(max_iterations, int) or max_iterations <= 0:
        raise ValueError("max_iterations harus bilangan bulat positif")

    start_time = time.perf_counter()
    used_fallback = False

    if initial_state is None:
        initial_state, used_fallback = random_initial_state(problem, rng)

    current = initial_state
    current_value = objective(current)

    best = current
    best_value = current_value

    # TODO: checkpoint berikutnya menambahkan loop dan cooling schedule.

    return {
        "algorithm": "sa",
        "initial_state": initial_state,
        "final_state": current,
        "best_state": best,
        "history": [current_value],
        "best_history": [best_value],
        "moves": [],
        "iterations": 0,
        "duration_s": time.perf_counter() - start_time,
        "used_fallback": used_fallback,
    }
