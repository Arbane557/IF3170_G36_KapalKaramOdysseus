from copy import deepcopy
from random import choice,random
from math import exp
def scoring(state: dict) -> float:
    return sum (
        package["value"] for package in state["packages"] if package.get("inTruck", True)
    )

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

def neighbors(state: dict) -> list[dict]:
    res = []
    direction = [
        (1,0,0),
        (-1,0,0),
        (0,1,0),
        (0,-1,0),
        (0,0,1),
        (0,0,-1)
    ]
    rotation_neighbors = {
        0: (1, 3, 4),
        1: (0, 2, 5),
        2: (1, 3, 4),
        3: (0, 2, 5),
        4: (0, 2, 5),
        5: (1, 3, 4),
    }

    for i, package in enumerate(state["packages"]):
        if package.get("inTruck", True):
            for d in direction:
                n = deepcopy(state)

                new_package = {
                    "x" : package["position"]["x"] + d[0],
                    "y" : package["position"]["y"] + d[1],
                    "z" : package["position"]["z"] + d[2]
                }

                n["packages"][i]["position"] = new_package

                if isvalid(n):
                    res.append(n)

            for orientation in rotation_neighbors[package.get("orientation", 0)]:
                rotated = deepcopy(state)
                rotated["packages"][i]["orientation"] = orientation

                if isvalid(rotated):
                    res.append(rotated)

            removed = deepcopy(state)
            removed["packages"][i]["inTruck"] = False
            if isvalid(removed):
                res.append(removed)

        else:
            package_dim = curr_dimension(package)
            truck_dim = state["truck"]["dimensions"]

            for orientation in range(6):
                oriented_package = deepcopy(package)
                oriented_package["orientation"] = orientation
                package_dim = curr_dimension(oriented_package)

                max_x = truck_dim["w"] - package_dim["w"]
                max_y = truck_dim["h"] - package_dim["h"]
                max_z = truck_dim["l"] - package_dim["l"]

                if max_x < 0 or max_y < 0 or max_z < 0:
                    continue

                for x in range(0, max_x + 1):
                    for y in range(0, max_y + 1):
                        for z in range(0, max_z + 1):
                            n = deepcopy(state)

                            new_package = {
                                "x" : x,
                                "y" : y,
                                "z" : z
                            }

                            n["packages"][i]["orientation"] = orientation
                            n["packages"][i]["position"] = new_package
                            n["packages"][i]["inTruck"] = True

                            if isvalid(n):
                                res.append(n)

    for i in range(len(state["packages"])):
        for j in range(i + 1, len(state["packages"])):
            swapped = deepcopy(state)
            swapped["packages"][i]["position"], swapped["packages"][j]["position"] = (
                swapped["packages"][j]["position"],
                swapped["packages"][i]["position"],
            )
            swapped["packages"][i]["inTruck"], swapped["packages"][j]["inTruck"] = (
                swapped["packages"][j].get("inTruck", True),
                swapped["packages"][i].get("inTruck", True),
            )

            if isvalid(swapped):
                res.append(swapped)

    return res

def solve(board: dict, temperature: float = 100, cooling_rate: float = 0.95, max_iter: int = 1000 ) -> dict:
    curr = deepcopy(board)
    init = deepcopy(curr)
    history = []

    for iteration in range(0, max_iter):
        temperature*=cooling_rate
        next=choice(neighbors(curr))
        delta_E=scoring(next)-scoring(curr)
        if(delta_E>0):
            curr = next
        elif(random()<exp(delta_E/T)):
            curr = next
        history.append({
            "iteration" : iteration + 1,
            "score" : scoring(curr),
            "state" : deepcopy(curr)
        })

    return {
        "init" : init,
        "steps" : history,
        "final" : curr,
        "initScore" : scoring(init),
        "finalScore" : scoring(curr),
        "iterations" : len(history)
    }
