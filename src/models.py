HORIZONTAL = "Horizontal"
VERTICAL = "Vertical"


def span(center, n):
    return range(center - (n - 1) // 2, center + n // 2 + 1)


class Vehicle:

    def __init__(self, vehicle_id, w, l, fee, weight, eta):
        self.id = vehicle_id
        self.w = w
        self.l = l
        self.fee = fee
        self.weight = weight
        self.eta = eta

    def extent(self, orientation):
        if orientation == HORIZONTAL:
            return self.l, self.w
        return self.w, self.l


class Ship:

    def __init__(self, w, l, max_capacity):
        self.w = w
        self.l = l
        self.max_capacity = max_capacity


class Problem:

    def __init__(self, vehicles, ships):
        self.vehicles = vehicles
        self.ships = ships


class State:
    def __init__(self, problem, positions, orientations):
        self.problem = problem
        self.positions = positions
        self.orientations = orientations

    @classmethod
    def empty(cls, problem):
        n = len(problem.vehicles)
        return cls(problem, [None] * n, [None] * n)

    def copy(self):
        return State(self.problem, list(self.positions), list(self.orientations))

    def is_inside(self, i):
        return self.positions[i] is not None

    def cells(self, i):
        if not self.is_inside(i):
            return []
        _, cx, cy = self.positions[i]
        dx, dy = self.problem.vehicles[i].extent(self.orientations[i])
        return [(x, y) for y in span(cy, dy) for x in span(cx, dx)]