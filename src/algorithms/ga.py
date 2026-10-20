from src.constraints import is_valid
from src.initial import random_initial_state
from src.models import State
from src.neighbors import get_random_neighbor


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
