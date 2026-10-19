from copy import deepcopy
from random import choice,random,randrange,_inst
from math import exp
from time import perf_counter
from algo.common import create_random_individual, scoring, isvalid, curr_dimension

def gen_random_suc(curr):
    while(True):
        i = choice([k for k, _ in enumerate(curr["packages"])])
        package= curr["packages"][i]
        truck_dim = curr["truck"]["dimensions"]

        do_swap, do_move, do_rotate = [random() < 0.5 for _ in range(3)]
        if(not (do_swap or do_move or do_rotate)):
            continue

        orientation= choice([o for o in range(6) if o != package["orientation"]]) if do_rotate else package["orientation"]
        rotated = deepcopy(package)
        rotated["orientation"] = orientation
        dim = curr_dimension(rotated)

        if(truck_dim["w"] - dim["w"] + 1<=0 or truck_dim["h"] - dim["h"] + 1<=0 or truck_dim["l"] - dim["l"] + 1<=0):
            continue
        position = package["position"]
        if(do_move):
            x=randrange(truck_dim["w"] - dim["w"] + 1)
            y=randrange(truck_dim["h"] - dim["h"] + 1)
            z=randrange(truck_dim["l"] - dim["l"] + 1)
            position = {"x": x, "y": y, "z": z}

        candidate = deepcopy(curr)
        candidate["packages"][i]["orientation"] = orientation
        candidate["packages"][i]["position"] = position

        if(do_swap):
            if(len(curr["packages"]) < 2):
                continue
            j = choice([k for k, _ in enumerate(curr["packages"]) if k != i])
            a, b = candidate["packages"][i], candidate["packages"][j]
            for key in ["position", "orientation", "inTruck"]:
                a[key], b[key] = b[key], a[key]

        if(isvalid(candidate)):
            break
    return candidate
def solve(board: dict, temperature: float = 100, cooling_rate: float = 0.95, max_iter: int = 1000 ) -> dict:
    started_at = perf_counter()
    curr = create_random_individual(board,_inst)
    init = deepcopy(curr)
    history = []

    for iteration in range(0, max_iter):
        temperature*=cooling_rate
        successor=gen_random_suc(curr)
        delta_E=scoring(successor)-scoring(curr)

        if temperature <= 0:
            if delta_E > 0:
                exponential_value = None
            else:
                exponential_value = 1.0 if delta_E == 0 else 0.0
        else:
            exponent = delta_E / temperature
            try:
                exponential_value = exp(exponent)
            except OverflowError:
                exponential_value = None

        acceptance_probability = 1.0 if delta_E >= 0 else (exponential_value or 0.0)
        accepted = delta_E >= 0 or random() < acceptance_probability
        if accepted:
            curr = successor

        history.append({
            "iteration" : iteration + 1,
            "score" : scoring(curr),
            "deltaScore": delta_E,
            "temperature": temperature,
            "expDeltaOverTemperature": exponential_value,
            "acceptanceProbability": acceptance_probability,
            "accepted": accepted,
            "state" : deepcopy(curr)
        })

    return {
        "init" : init,
        "steps" : history,
        "final" : curr,
        "initScore" : scoring(init),
        "finalScore" : scoring(curr),
        "iterations" : len(history),
        "duration": perf_counter() - started_at,
    }
