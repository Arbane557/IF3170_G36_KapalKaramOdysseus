from copy import deepcopy
from random import Random
from time import perf_counter

def scoring(state: dict) -> float:
    packages = [package for package in state["packages"] if package.get("inTruck", True)]

    if state.get("scoringMode") == "value_eta":
        return sum(
            package["value"] + package["value"] / max(package.get("eta", 1), 1)
            for package in packages
        )

    return sum(package["value"] for package in packages)

def curr_dimension(package: dict) -> dict:
    w, h, l = package["dimensions"]["w"], package["dimensions"]["h"], package["dimensions"]["l"]

    orientations = [
        {"w": w, "l": l, "h": h},
        {"w": w, "l": h, "h": l},
        {"w": h, "l": w, "h": l},
        {"w": h, "l": l, "h": w},
        {"w": l, "l": w, "h": h},
        {"w": l, "l": h, "h": w},
    ]

    orientation = package.get("orientation", 0)

    if orientation < 0 or orientation >= len(orientations):
        raise ValueError(f"idk why I need this")

    return orientations[orientation]

def cek_overlap(a: dict, b: dict) -> bool:
    a_pos = a["position"]
    a_dim = curr_dimension(a)
    b_pos = b["position"]
    b_dim = curr_dimension(b)

    overlap_x = not (a_pos["x"] + a_dim["w"] <= b_pos["x"] or b_pos["x"] + b_dim["w"] <= a_pos["x"])
    overlap_y = not (a_pos["y"] + a_dim["h"] <= b_pos["y"] or b_pos["y"] + b_dim["h"] <= a_pos["y"])
    overlap_z = not (a_pos["z"] + a_dim["l"] <= b_pos["z"] or b_pos["z"] + b_dim["l"] <= a_pos["z"])

    return overlap_x and overlap_y and overlap_z

def raycast_below_for_fragile_or_support(state: dict, package: dict) -> bool:
    pos = package["position"]
    dim = curr_dimension(package)

    if pos["y"] == 0:
        return False

    has_support = False

    for x in range(pos["x"], pos["x"] + dim["w"]):
        for z in range(pos["z"], pos["z"] + dim["l"]):
            for other in state["packages"]:
                if other["id"] == package["id"]:
                    continue

                if not other.get("inTruck", True):
                    continue

                other_pos = other["position"]
                other_dim = curr_dimension(other)

                directly_below = other_pos["y"] + other_dim["h"] == pos["y"]
                covers_point = (
                    other_pos["x"] <= x < other_pos["x"] + other_dim["w"]
                    and other_pos["z"] <= z < other_pos["z"] + other_dim["l"]
                )

                if directly_below and covers_point:
                    if other.get("isFragile", False):
                        return True

                    has_support = True
                    break

    return not has_support

def isvalid(state: dict) -> bool:
    truck = state["truck"]
    truck_dim = truck["dimensions"]

    inside = [
        package for package in state["packages"] if package.get("inTruck", True)
    ]

    total_weight = sum(package["weight"] for package in inside)

    if total_weight > truck["maxCapacity"]:
        return False

    for package in inside:
        pos = package["position"]
        dim = curr_dimension(package)

        if pos["x"] < 0 or pos["y"] < 0 or pos["z"] < 0:
            return False

        if pos["x"] + dim["w"] > truck_dim["w"]:
            return False

        if pos["y"] + dim["h"] > truck_dim["h"]:
            return False

        if pos["z"] + dim["l"] > truck_dim["l"]:
            return False

        if raycast_below_for_fragile_or_support(state, package):
            return False

    for i in range (len(inside)):
        for j in range(i + 1, len(inside)):
            if cek_overlap(inside[i], inside[j]):
                return False

    return True

def empty_state(board: dict) -> dict:
    state = deepcopy(board)
    for package in state["packages"]:
        package["inTruck"] = False
    return state


def place_at(
    state: dict,
    package_index: int,
    orientation: int,
    position: dict[str, int],
) -> bool:
    package = state["packages"][package_index]
    package["orientation"] = orientation
    package["position"] = position
    package["inTruck"] = True
    return isvalid(state)


def find_random_valid_placement(state: dict, package_index: int, rng: Random) -> bool:
    truck_dimensions = state["truck"]["dimensions"]
    orientations = list(range(6))
    rng.shuffle(orientations)

    for orientation in orientations:
        package = deepcopy(state["packages"][package_index])
        package["orientation"] = orientation
        dimensions = curr_dimension(package)
        max_x = truck_dimensions["w"] - dimensions["w"]
        max_y = truck_dimensions["h"] - dimensions["h"]
        max_z = truck_dimensions["l"] - dimensions["l"]

        if max_x < 0 or max_y < 0 or max_z < 0:
            continue

        positions = [
            {"x": x, "y": y, "z": z}
            for x in range(max_x + 1)
            for y in range(max_y + 1)
            for z in range(max_z + 1)
        ]
        rng.shuffle(positions)

        for position in positions:
            candidate = deepcopy(state)
            if place_at(candidate, package_index, orientation, position):
                state.clear()
                state.update(candidate)
                return True

    return False


def create_random_individual(board: dict, rng: Random) -> dict:
    individual = empty_state(board)
    package_indices = list(range(len(individual["packages"])))
    rng.shuffle(package_indices)

    for package_index in package_indices:
        if rng.random() < 0.50:
            find_random_valid_placement(individual, package_index, rng)

    return individual
