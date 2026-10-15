from src.models import State, HORIZONTAL, VERTICAL
from src.constraints import is_valid


def random_position(problem, i, orientation, rng):
    dx, dy = problem.vehicles[i].extent(orientation)
    ship = rng.randrange(len(problem.ships))
    deck = problem.ships[ship]
    if dx > deck.l or dy > deck.w:
        return None
    x = rng.randint((dx - 1) // 2, deck.l - 1 - dx // 2)
    y = rng.randint((dy - 1) // 2, deck.w - 1 - dy // 2)
    return (ship, x, y)


def random_attempt(problem, rng, p):
    state = State.empty(problem)
    for i in range(len(problem.vehicles)):
        if rng.random() < p:
            orientation = rng.choice([HORIZONTAL, VERTICAL])
            pos = random_position(problem, i, orientation, rng)
            if pos is not None:
                state.positions[i] = pos
                state.orientations[i] = orientation
    return state


def all_positions(problem, i):
    result = []
    for ship, deck in enumerate(problem.ships):
        for orientation in (HORIZONTAL, VERTICAL):
            dx, dy = problem.vehicles[i].extent(orientation)
            for y in range((dy - 1) // 2, deck.w - dy // 2):
                for x in range((dx - 1) // 2, deck.l - dx // 2):
                    result.append((ship, x, y, orientation))
    return result


def fallback_state(problem, rng):
    state = State.empty(problem)
    order = list(range(len(problem.vehicles)))
    rng.shuffle(order)
    for i in order:
        options = all_positions(problem, i)
        rng.shuffle(options)
        for ship, x, y, orientation in options:
            state.positions[i] = (ship, x, y)
            state.orientations[i] = orientation
            if is_valid(state):
                break
            state.positions[i] = None
            state.orientations[i] = None
    return state


def random_initial_state(problem, rng, p=0.3, max_tries=500):
    for _ in range(max_tries):
        state = random_attempt(problem, rng, p)
        if is_valid(state):
            return state, False
    return fallback_state(problem, rng), True