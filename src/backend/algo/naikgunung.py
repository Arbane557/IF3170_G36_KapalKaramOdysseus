from copy import deepcopy
from random import choice,randrange,_inst
from algo.common import create_random_individual, scoring, isvalid, curr_dimension

def solve_steepest(board: dict, max_iter: int = 100) -> dict:
    curr = create_random_individual(board,_inst)
    init = deepcopy(curr)
    history = []

    for iteration in range(0, max_iter):
        best = None
        best_value = -1

        for i, package in enumerate(curr["packages"]):
            if package.get("inTruck", True):
                continue

            found = False
            truck_dim = curr["truck"]["dimensions"]

            for orientation in range(6):
                rotated = deepcopy(package)
                rotated["orientation"] = orientation
                dim = curr_dimension(rotated)

                for x in range(truck_dim["w"] - dim["w"] + 1):
                    for y in range(truck_dim["h"] - dim["h"] + 1):
                        for z in range(truck_dim["l"] - dim["l"] + 1):
                            candidate = deepcopy(curr)
                            candidate["packages"][i]["orientation"] = orientation
                            candidate["packages"][i]["position"] = {"x": x, "y": y, "z": z}
                            candidate["packages"][i]["inTruck"] = True

                            if isvalid(candidate):
                                if package["value"] > best_value:
                                    best = candidate
                                    best_value = package["value"]
                                found = True
                                break

                        if found:
                            break
                    if found:
                        break
                if found:
                    break

        if best is None:
            break

        if scoring(best) <= scoring(curr):
            break

        curr = best

        history.append({
            "iteration" : iteration + 1,
            "score" : scoring(curr),
            "state" : deepcopy(curr)
        })

    return {
        "algorithm" : "hill-climbing-steepest",
        "implemented" : True,
        "init" : init,
        "steps" : history,
        "final" : curr,
        "initScore" : scoring(init),
        "finalScore" : scoring(curr),
        "iterations" : len(history)
    }

def gen_random_suc(curr):
    while(True):
        i = choice([k for k, _ in enumerate(curr["packages"])])
        package= curr["packages"][i]
        truck_dim = curr["truck"]["dimensions"]

        orientation= choice(range(6))
        rotated = deepcopy(package)
        rotated["orientation"] = orientation
        dim = curr_dimension(rotated)
        if(truck_dim["w"] - dim["w"] + 1<=0 or truck_dim["h"] - dim["h"] + 1<=0 or truck_dim["l"] - dim["l"] + 1<=0):
            continue
        x=randrange(truck_dim["w"] - dim["w"] + 1)
        y=randrange(truck_dim["h"] - dim["h"] + 1)
        z=randrange(truck_dim["l"] - dim["l"] + 1)

        candidate = deepcopy(curr)
        candidate["packages"][i]["orientation"] = orientation
        candidate["packages"][i]["position"] = {"x": x, "y": y, "z": z}
        candidate["packages"][i]["inTruck"] = choice([True, False])
        if(isvalid(candidate)):
            break
    return candidate

def solve_stochastic(board: dict, max_iter: int = 100) -> dict:
    curr = create_random_individual(board,_inst)
    init = deepcopy(curr)
    history = []

    for iteration in range(0, max_iter):
        candidate = gen_random_suc(curr)

        if scoring(candidate) > scoring(curr):
            curr = candidate

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


def solve_sideways(board: dict, max_iter: int = 100, max_sideways: int = 20) -> dict:
    curr = create_random_individual(board,_inst)
    init = deepcopy(curr)
    history = []

    for iteration in range(0, max_iter):
        best = None
        best_value = -1

        for i, package in enumerate(curr["packages"]):
            if package.get("inTruck", True):
                continue

            found = False
            truck_dim = curr["truck"]["dimensions"]

            for orientation in range(6):
                rotated = deepcopy(package)
                rotated["orientation"] = orientation
                dim = curr_dimension(rotated)

                for x in range(truck_dim["w"] - dim["w"] + 1):
                    for y in range(truck_dim["h"] - dim["h"] + 1):
                        for z in range(truck_dim["l"] - dim["l"] + 1):
                            candidate = deepcopy(curr)
                            candidate["packages"][i]["orientation"] = orientation
                            candidate["packages"][i]["position"] = {"x": x, "y": y, "z": z}
                            candidate["packages"][i]["inTruck"] = True

                            if isvalid(candidate):
                                if package["value"] > best_value:
                                    best = candidate
                                    best_value = package["value"]
                                found = True
                                break

                        if found:
                            break
                    if found:
                        break
                if found:
                    break

        if best is None:
            break

        if scoring(best) < scoring(curr):
            break

        curr = best

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


def solve_random_restart(board: dict, max_iter: int = 100, max_restart: int = 10) -> dict:
    curr = create_random_individual(board,_inst)
    init = deepcopy(curr)
    history = []
    for iteration in range(0, max_restart):
        curr = create_random_individual(board,_inst)
        for iteration in range(0, max_iter):
            best = None
            best_value = -1

            for i, package in enumerate(curr["packages"]):
                if package.get("inTruck", True):
                    continue

                found = False
                truck_dim = curr["truck"]["dimensions"]

                for orientation in range(6):
                    rotated = deepcopy(package)
                    rotated["orientation"] = orientation
                    dim = curr_dimension(rotated)

                    for x in range(truck_dim["w"] - dim["w"] + 1):
                        for y in range(truck_dim["h"] - dim["h"] + 1):
                            for z in range(truck_dim["l"] - dim["l"] + 1):
                                candidate = deepcopy(curr)
                                candidate["packages"][i]["orientation"] = orientation
                                candidate["packages"][i]["position"] = {"x": x, "y": y, "z": z}
                                candidate["packages"][i]["inTruck"] = True

                                if isvalid(candidate):
                                    if package["value"] > best_value:
                                        best = candidate
                                        best_value = package["value"]
                                    found = True
                                    break

                            if found:
                                break
                        if found:
                            break
                    if found:
                        break

            if best is None:
                break

            if scoring(best) <= scoring(curr):
                break

            curr = best

            history.append({
                "iteration" : iteration + 1,
                "score" : scoring(curr),
                "state" : deepcopy(curr)
            })

    return {
        "algorithm" : "hill-climbing-random-restart",
        "implemented" : True,
        "init" : init,
        "steps" : history,
        "final" : curr,
        "initScore" : scoring(init),
        "finalScore" : scoring(curr),
        "iterations" : len(history)
    }


