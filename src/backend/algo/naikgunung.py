from copy import deepcopy
from random import randint

def scoring(state: dict) -> float:
    return sum (
        package["value"] for package in state["packages"] if package.get("inTruck", True)
    )
    
def cek_overlap(a: dict, b: dict) -> bool:
    a_pos = a["position"]
    a_dim = a["dimensions"]
    b_pos = b["position"]
    b_dim = b["dimensions"]
    
    overlap_x = not (a_pos["x"] + a_dim["w"] <= b_pos["x"] or b_pos["x"] + b_dim["w"] <= a_pos["x"])
    overlap_y = not (a_pos["y"] + a_dim["h"] <= b_pos["y"] or b_pos["y"] + b_dim["h"] <= a_pos["y"])
    overlap_z = not (a_pos["z"] + a_dim["l"] <= b_pos["z"] or b_pos["z"] + b_dim["l"] <= a_pos["z"])    
    
    return overlap_x and overlap_y and overlap_z

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
        dim = package["dimensions"]
        
        if pos["x"] < 0 or pos["y"] < 0 or pos["z"] < 0:
            return False
        
        if pos["x"] + dim["w"] > truck_dim["w"]:
            return False
        
        if pos["y"] + dim["h"] > truck_dim["h"]:
            return False
        
        if pos["z"] + dim["l"] > truck_dim["l"]:
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
        else:
            package_dim = package["dimensions"]
            truck_dim = state["truck"]["dimensions"]
            
            max_x = truck_dim["w"] - package_dim["w"]
            max_y = truck_dim["h"] - package_dim["h"]
            max_z = truck_dim["l"] - package_dim["l"]
            
            for x in range(0, max_x + 1):
                for y in range(0, max_y + 1):
                    for z in range(0, max_z + 1):
                        n = deepcopy(state)
                        
                        new_package = {
                            "x" : x,
                            "y" : y,
                            "z" : z
                        }
                        
                        n["packages"][i]["position"] = new_package
                        n["packages"][i]["inTruck"] = True
                        
                        if isvalid(n):
                            res.append(n)
        
    return res
            

def solve(board: dict, max_iter: int = 100) -> dict:
    curr = deepcopy(board)
    init = deepcopy(curr)
    history = []
    
    for iteration in range(0, max_iter):
        new_neighbors = neighbors(curr)
        
        if (not new_neighbors):
            break
        
        best = max(new_neighbors, key=scoring)
        
        if scoring(best) <= scoring(curr):
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
    