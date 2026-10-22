import time

from src.constraints import is_valid
from src.initial import random_initial_state
from src.models import State
from src.neighbors import get_random_neighbor
from src.objective import objective


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
