import json

from src.models import Vehicle, Ship, Problem


def load_problem(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    ships = [
        Ship(s["Dimensions"]["w"], s["Dimensions"]["l"], s["MaxCapacity"])
        for s in data["ships"]
    ]
    vehicles = [
        Vehicle(
            v["id"],
            v["Dimensions"]["w"],
            v["Dimensions"]["l"],
            v["ShippingFee"],
            v["Weight"],
            v["ETA"],
        )
        for v in data["vehicles"]
    ]
    return Problem(vehicles, ships)