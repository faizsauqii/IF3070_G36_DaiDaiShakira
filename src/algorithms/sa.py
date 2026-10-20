"""Simulated Annealing untuk masalah penempatan kendaraan.
"""

import time
import math

from src.initial import random_initial_state
from src.objective import objective
from src.neighbors import get_random_neighbor

def cooling_schedule(t, initial_temp, cooling_rate, max_iterations):
    # Hitung temperatur SA menggunakan geometric cooling

    # Cek indeks iterasi tidak boleh negatif atau bukan bil. bulat
    if not isinstance(t, int) or t < 0:
        raise ValueError("Indeks iterasi harus bilangan bulat non-negatif")

    if t >= max_iterations:
        return 0.0

    return initial_temp * (cooling_rate ** t)

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

    history = [current_value]
    best_history = [best_value]
    moves = []
    iterations = 0

    for t in range(max_iterations):
        temperature = cooling_schedule(
            t,
            initial_temp,
            cooling_rate,
            max_iterations,
        )

        if temperature <= 0:
            break

        move, neighbor = get_random_neighbor(current, rng)

        if neighbor is not None:
            neighbor_value = objective(neighbor)
            delta_e = neighbor_value - current_value

            if delta_e >= 0:
                accepted = True
            else:
                probability = math.exp(delta_e / temperature)
                accepted = rng.random() < probability

            if accepted:
                current = neighbor
                current_value = neighbor_value
                moves.append(move)

                if current_value > best_value:
                    best = current
                    best_value = current_value

        iterations += 1
        history.append(current_value)
        best_history.append(best_value)

    return {
        "algorithm": "sa",
        "initial_state": initial_state,
        "final_state": current,
        "best_state": best,
        "history": history,
        "best_history": best_history,
        "moves": moves,
        "iterations": iterations,
        "duration_s": time.perf_counter() - start_time,
        "used_fallback": used_fallback,
    }
