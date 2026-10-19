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
