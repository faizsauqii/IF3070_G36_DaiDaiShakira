from src.initial import random_initial_state


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
