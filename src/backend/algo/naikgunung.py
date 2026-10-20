from copy import deepcopy
from random import choice,randrange,_inst
from time import perf_counter
from algo.common import create_random_individual, scoring, isvalid, curr_dimension

def generate_neighbors(state: dict) -> list[dict]:
    neighbors = []
    packages = state["packages"]
    truck_dim = state["truck"]["dimensions"]

    for i in range(len(packages)):
        for j in range(i + 1, len(packages)):
            if not packages[i].get("inTruck", False) and not packages[j].get("inTruck", False):
                continue
            candidate = deepcopy(state)
            a, b = candidate["packages"][i], candidate["packages"][j]
            a["position"], b["position"] = b["position"], a["position"]
            a["inTruck"], b["inTruck"] = b.get("inTruck", False), a.get("inTruck", False)
            if candidate != state and isvalid(candidate):
                neighbors.append(candidate)

    for i, package in enumerate(packages):
        dim = curr_dimension(package)
        for x in range(truck_dim["w"] - dim["w"] + 1):
            for y in range(truck_dim["h"] - dim["h"] + 1):
                for z in range(truck_dim["l"] - dim["l"] + 1):
                    position = {"x": x, "y": y, "z": z}
                    if package.get("inTruck", False) and package["position"] == position:
                        continue
                    candidate = deepcopy(state)
                    candidate["packages"][i]["position"] = position
                    candidate["packages"][i]["inTruck"] = True
                    if isvalid(candidate):
                        neighbors.append(candidate)

    for i, package in enumerate(packages):
        for orientation in range(6):
            if orientation == package.get("orientation", 0):
                continue
            candidate = deepcopy(state)
            candidate["packages"][i]["orientation"] = orientation
            if isvalid(candidate):
                neighbors.append(candidate)

    return neighbors

def solve_steepest(board: dict, max_iter: int = 100) -> dict:
    curr = create_random_individual(board,_inst)
    init = deepcopy(curr)
    history = []

    for iteration in range(0, max_iter):
        neighbors = generate_neighbors(curr)
        if not neighbors:
            break

        best = max(neighbors, key=scoring)

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

        action = choice(["swap", "move", "rotate"])

        if(action=="rotate" and not package.get("inTruck", False)):
            continue

        orientation= choice([o for o in range(6) if o != package["orientation"]]) if action=="rotate" else package["orientation"]
        rotated = deepcopy(package)
        rotated["orientation"] = orientation
        dim = curr_dimension(rotated)

        if(truck_dim["w"] - dim["w"] + 1<=0 or truck_dim["h"] - dim["h"] + 1<=0 or truck_dim["l"] - dim["l"] + 1<=0):
            continue
        position = package["position"]
        if(action=="move"):
            x=randrange(truck_dim["w"] - dim["w"] + 1)
            y=randrange(truck_dim["h"] - dim["h"] + 1)
            z=randrange(truck_dim["l"] - dim["l"] + 1)
            position = {"x": x, "y": y, "z": z}
            if(package.get("inTruck", False) and position == package["position"]):
                continue

        candidate = deepcopy(curr)
        candidate["packages"][i]["orientation"] = orientation
        candidate["packages"][i]["position"] = position
        if(action=="move"):
            candidate["packages"][i]["inTruck"] = True

        if(action=="swap"):
            if(len(curr["packages"]) < 2):
                continue
            j = choice([k for k, _ in enumerate(curr["packages"]) if k != i])
            if(not curr["packages"][i].get("inTruck", False) and not curr["packages"][j].get("inTruck", False)):
                continue
            a, b = candidate["packages"][i], candidate["packages"][j]
            for key in ["position", "inTruck"]:
                a[key], b[key] = b[key], a[key]

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
        neighbors = generate_neighbors(curr)
        if not neighbors:
            break

        best = max(neighbors, key=scoring)

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
    started_at = perf_counter()
    curr = None
    init = None
    history = []
    restart_stats = []
    total_iterations = 0

    for restart_number in range(1, max_restart + 1):
        restart_started_at = perf_counter()
        curr = create_random_individual(board,_inst)
        if init is None:
            init = deepcopy(curr)

        history.append({
            "iteration": len(history) + 1,
            "restart": restart_number,
            "restartIteration": 0,
            "restartStarted": True,
            "score": scoring(curr),
            "state": deepcopy(curr),
        })

        iterations_this_restart = 0
        for restart_iteration in range(1, max_iter + 1):
            iterations_this_restart = restart_iteration
            total_iterations += 1
            neighbors = generate_neighbors(curr)
            if not neighbors:
                break

            best = max(neighbors, key=scoring)

            if scoring(best) <= scoring(curr):
                break

            curr = best

            history.append({
                "iteration": len(history) + 1,
                "restart": restart_number,
                "restartIteration": restart_iteration,
                "restartStarted": False,
                "score": scoring(curr),
                "state": deepcopy(curr),
            })

        restart_stats.append({
            "restart": restart_number,
            "iterations": iterations_this_restart,
            "score": scoring(curr),
            "duration": perf_counter() - restart_started_at,
        })

    if init is None:
        curr = create_random_individual(board,_inst)
        init = deepcopy(curr)

    return {
        "algorithm" : "hill-climbing-random-restart",
        "implemented" : True,
        "init" : init,
        "steps" : history,
        "final" : curr,
        "initScore" : scoring(init),
        "finalScore" : scoring(curr),
        "iterations" : total_iterations,
        "restarts": len(restart_stats),
        "maxRestart": max_restart,
        "iterationsPerRestart": [item["iterations"] for item in restart_stats],
        "restartStats": restart_stats,
        "duration": perf_counter() - started_at,
    }


