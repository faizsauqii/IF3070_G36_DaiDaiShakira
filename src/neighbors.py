from src.models import HORIZONTAL, VERTICAL
from src.constraints import is_valid

DIRECTIONS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


def apply_move(state, move):
    new = state.copy()
    kind, i = move[0], move[1]
    if kind == "swap":
        j = move[2]
        new.positions[i], new.positions[j] = state.positions[j], state.positions[i]
        new.orientations[i], new.orientations[j] = state.orientations[j], state.orientations[i]
    elif kind == "shift":
        ship, x, y = state.positions[i]
        dx, dy = DIRECTIONS[move[2]]
        new.positions[i] = (ship, x + dx, y + dy)
    elif kind == "rotate":
        new.orientations[i] = VERTICAL if state.orientations[i] == HORIZONTAL else HORIZONTAL
    elif kind == "remove":
        new.positions[i] = None
        new.orientations[i] = None
    elif kind == "insert":
        new.positions[i] = move[2]
        new.orientations[i] = HORIZONTAL
    return new


def all_moves(state):
    n = len(state.problem.vehicles)
    inside = [i for i in range(n) if state.is_inside(i)]
    outside = [i for i in range(n) if not state.is_inside(i)]
    moves = []
    for a in range(n):
        for b in range(a + 1, n):
            if state.is_inside(a) or state.is_inside(b):
                moves.append(("swap", a, b))
    for i in inside:
        for direction in DIRECTIONS:
            moves.append(("shift", i, direction))
        moves.append(("rotate", i))
        moves.append(("remove", i))
    for i in outside:
        for ship, deck in enumerate(state.problem.ships):
            for y in range(deck.w):
                for x in range(deck.l):
                    moves.append(("insert", i, (ship, x, y)))
    return moves


def get_all_neighbors(state):
    result = []
    for move in all_moves(state):
        new = apply_move(state, move)
        if is_valid(new):
            result.append((move, new))
    return result


def random_move(state, rng):
    n = len(state.problem.vehicles)
    inside = [i for i in range(n) if state.is_inside(i)]
    outside = [i for i in range(n) if not state.is_inside(i)]
    kinds = []
    if inside and n > 1:
        kinds.append("swap")
    if inside:
        kinds += ["shift", "rotate", "remove"]
    if outside:
        kinds.append("insert")
    kind = rng.choice(kinds)
    if kind == "swap":
        i = rng.choice(inside)
        j = rng.choice([k for k in range(n) if k != i])
        return ("swap", i, j)
    if kind == "shift":
        return ("shift", rng.choice(inside), rng.choice(list(DIRECTIONS)))
    if kind == "rotate":
        return ("rotate", rng.choice(inside))
    if kind == "remove":
        return ("remove", rng.choice(inside))
    ship = rng.randrange(len(state.problem.ships))
    deck = state.problem.ships[ship]
    return ("insert", rng.choice(outside), (ship, rng.randrange(deck.l), rng.randrange(deck.w)))


def get_random_neighbor(state, rng):
    move = random_move(state, rng)
    new = apply_move(state, move)
    if is_valid(new):
        return move, new
    return move, None


def describe_move(problem, move):
    kind, i = move[0], move[1]
    name = problem.vehicles[i].id
    if kind == "swap":
        return f"swap {name} <-> {problem.vehicles[move[2]].id}"
    if kind == "shift":
        return f"shift {name} {move[2]}"
    if kind == "insert":
        ship, x, y = move[2]
        return f"insert {name} at ship {ship} ({x}, {y})"
    return f"{kind} {name}"