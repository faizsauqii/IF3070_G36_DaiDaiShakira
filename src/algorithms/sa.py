"""Simulated Annealing untuk masalah penempatan kendaraan.
"""

import time
import math

from src.initial import random_initial_state
from src.objective import objective
from src.neighbors import get_all_neighbors, get_random_neighbor

def cooling_schedule(t, initial_temp, cooling_rate, max_iterations):
    # Hitung temperatur SA menggunakan geometric cooling

    # Cek indeks iterasi tidak boleh negatif atau bukan bil. bulat
    if not isinstance(t, int) or t < 0:
        raise ValueError("Indeks iterasi harus bilangan bulat non-negatif")

    if t >= max_iterations:
        return 0.0

    return initial_temp * (cooling_rate ** t)


def is_local_maximum(state):
    """Periksa apakah state tidak memiliki neighbor valid yang lebih baik."""

    current_value = objective(state)

    for move, neighbor in get_all_neighbors(state):
        neighbor_value = objective(neighbor)

        if neighbor_value > current_value:
            return False

    return True

def count_stuck_episodes(visited_states):
    """Hitung episode ketika pencarian berada di local maximum."""

    stuck_count = 0
    was_local_maximum = False

    for state in visited_states:
        current_is_local_maximum = is_local_maximum(state)

        if current_is_local_maximum and not was_local_maximum:
            stuck_count += 1

        was_local_maximum = current_is_local_maximum

    return stuck_count

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
    visited_states = [current]
    temperature_history = []
    delta_history = []
    acceptance_probability_history = []
    accepted_history = []

    invalid_neighbors = 0
    accepted_worse_moves = 0


    for t in range(max_iterations):
        temperature = cooling_schedule(
            t,
            initial_temp,
            cooling_rate,
            max_iterations,
        )

        if temperature <= 0:
            break



        temperature_history.append(temperature)

        move, neighbor = get_random_neighbor(current, rng)

        # Nilai default untuk neighbor yang tidak valid.
        delta_e = None
        acceptance_probability = None
        accepted = False

        if neighbor is None:
            invalid_neighbors += 1

        else:
            neighbor_value = objective(neighbor)
            delta_e = neighbor_value - current_value

            if delta_e >= 0:
                acceptance_probability = 1.0
                accepted = True
            else:
                acceptance_probability = math.exp(
                    delta_e / temperature
                )
                accepted = (
                    rng.random() < acceptance_probability
                )

            if accepted:
                if delta_e < 0:
                    accepted_worse_moves += 1

                current = neighbor
                current_value = neighbor_value
                moves.append(move)
                visited_states.append(current)

                if current_value > best_value:
                    best = current
                    best_value = current_value

        delta_history.append(delta_e)
        acceptance_probability_history.append(
            acceptance_probability
        )
        accepted_history.append(accepted)

        iterations += 1
        history.append(current_value)
        best_history.append(best_value)

    # Durasi inti pencarian SA, tanpa diagnosis stuck.
    duration_s = time.perf_counter() - start_time

    # Diagnosis local maximum dilakukan setelah pencarian selesai.
    diagnosis_start = time.perf_counter()

    stuck_count = count_stuck_episodes(visited_states)

    diagnosis_duration_s = (
        time.perf_counter() - diagnosis_start
    )




    return {
        "algorithm": "sa",
        "params": {
            "initial_temp": initial_temp,
            "cooling_rate": cooling_rate,
            "max_iterations": max_iterations,
        },
        "initial_state": initial_state,
        "final_state": current,
        "best_state": best,
        "history": history,
        "best_history": best_history,
        "moves": moves,
        "iterations": iterations,
        "duration_s": duration_s,
        "used_fallback": used_fallback,
        "temperature_history": temperature_history,
        "delta_history": delta_history,
        "acceptance_probability_history": (
            acceptance_probability_history
        ),
        "accepted_history": accepted_history,
        "invalid_neighbors": invalid_neighbors,
        "invalid_neighbor_percentage": (
            100.0 * invalid_neighbors / iterations
            if iterations > 0 else 0.0
        ),
        "accepted_worse_moves": accepted_worse_moves,
        "stuck_count": stuck_count,
        "diagnosis_duration_s": diagnosis_duration_s,
    }
