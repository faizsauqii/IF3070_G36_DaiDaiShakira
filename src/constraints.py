def build_grid(state, ship):
    deck = state.problem.ships[ship]
    grid = [[None] * deck.l for _ in range(deck.w)]
    for i, pos in enumerate(state.positions):
        if pos is None or pos[0] != ship:
            continue
        for x, y in state.cells(i):
            if not (0 <= x < deck.l and 0 <= y < deck.w):
                return None
            if grid[y][x] is not None:
                return None
            grid[y][x] = i
    return grid


def total_weight(state, ship):
    return sum(
        vehicle.weight
        for vehicle, pos in zip(state.problem.vehicles, state.positions)
        if pos is not None and pos[0] == ship
    )


def is_valid(state):
    for ship, deck in enumerate(state.problem.ships):
        if build_grid(state, ship) is None:
            return False
        if total_weight(state, ship) > deck.max_capacity:
            return False
    return True