from src.constraints import build_grid


def total_fee(state):
    return sum(
        vehicle.fee
        for vehicle, pos in zip(state.problem.vehicles, state.positions)
        if pos is not None
    )


def largest_empty_rectangle(grid):
    heights = [0] * len(grid[0])
    best = 0
    for row in grid:
        for x, cell in enumerate(row):
            heights[x] = heights[x] + 1 if cell is None else 0
        for start in range(len(heights)):
            min_height = heights[start]
            for end in range(start, len(heights)):
                min_height = min(min_height, heights[end])
                if min_height == 0:
                    break
                best = max(best, min_height * (end - start + 1))
    return best


def tie_breaker(state):
    total = 0
    for ship, deck in enumerate(state.problem.ships):
        empty = largest_empty_rectangle(build_grid(state, ship))
        total += 0.99 * empty / (deck.w * deck.l)
    return total / len(state.problem.ships)


def objective(state):
    return total_fee(state) + tie_breaker(state)