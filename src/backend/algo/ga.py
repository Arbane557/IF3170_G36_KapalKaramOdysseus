from copy import deepcopy
from random import Random
from time import perf_counter

from algo.naikgunung import curr_dimension, isvalid, scoring

ROTATION_NEIGHBORS = {
    0: (1, 3, 4),
    1: (0, 2, 5),
    2: (1, 3, 4),
    3: (0, 2, 5),
    4: (0, 2, 5),
    5: (1, 3, 4),
}


def fitness(state: dict) -> float:
    return scoring(state)


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


def find_random_valid_position(state: dict, package_index: int, rng: Random) -> bool:
    truck_dimensions = state["truck"]["dimensions"]
    package = state["packages"][package_index]
    dimensions = curr_dimension(package)
    max_x = truck_dimensions["w"] - dimensions["w"]
    max_y = truck_dimensions["h"] - dimensions["h"]
    max_z = truck_dimensions["l"] - dimensions["l"]

    if max_x < 0 or max_y < 0 or max_z < 0:
        return False

    positions = [
        {"x": x, "y": y, "z": z}
        for x in range(max_x + 1)
        for y in range(max_y + 1)
        for z in range(max_z + 1)
    ]
    rng.shuffle(positions)

    for position in positions:
        candidate = deepcopy(state)
        if place_at(candidate, package_index, package["orientation"], position):
            state.clear()
            state.update(candidate)
            return True

    return False


def create_random_individual(board: dict, rng: Random) -> dict:
    individual = empty_state(board)
    package_indices = list(range(len(individual["packages"])))
    rng.shuffle(package_indices)

    for package_index in package_indices:
        if rng.random() < 0.75:
            find_random_valid_placement(individual, package_index, rng)

    if fitness(individual) == 0:
        for package_index in package_indices:
            if find_random_valid_placement(individual, package_index, rng):
                break

    return individual


def selection(population: list[dict], rng: Random) -> dict:
    total_fitness = 0

    for individual in population:
        total_fitness += fitness(individual)

    if total_fitness <= 0:
        return deepcopy(rng.choice(population))

    random_number = rng.uniform(0, total_fitness)
    cumulative_fitness = 0

    for individual in population:
        cumulative_fitness += fitness(individual)

        if random_number <= cumulative_fitness:
            return deepcopy(individual)

    return deepcopy(population[-1])

#pakai roulette wheel
def crossover(parent_a: dict, parent_b: dict, rng: Random) -> dict:
    child = empty_state(parent_a)
    package_count = len(child["packages"])

    if package_count < 2:
        crossover_point = package_count
    else:
        crossover_point = rng.randint(1, package_count - 1)

    for package_index in range(package_count):
        if package_index < crossover_point:
            parent = parent_a
        else:
            parent = parent_b

        package = parent["packages"][package_index]

        if not package.get("inTruck", False):
            continue

        candidate = deepcopy(child)
        if place_at(
            candidate,
            package_index,
            package.get("orientation", 0),
            deepcopy(package["position"]),
        ):
            child = candidate
        else:
            find_random_valid_placement(child, package_index, rng)

    return child

#random pakai satu point
def mutate(individual: dict, rng: Random, mutation_rate: float = 0.15) -> dict:
    mutated = deepcopy(individual)

    if rng.random() >= mutation_rate or not mutated["packages"]:
        return mutated

    operation = rng.choice(["move", "swap", "rotate"])
    package_count = len(mutated["packages"])

    if operation == "move":
        package_index = rng.randrange(package_count)
        trial = deepcopy(mutated)
        trial["packages"][package_index]["inTruck"] = False
        if find_random_valid_position(trial, package_index, rng):
            return trial

    elif operation == "swap" and package_count >= 2:
        first, second = rng.sample(range(package_count), 2)
        trial = deepcopy(mutated)
        trial["packages"][first]["position"], trial["packages"][second]["position"] = (
            trial["packages"][second]["position"],
            trial["packages"][first]["position"],
        )
        trial["packages"][first]["inTruck"], trial["packages"][second]["inTruck"] = (
            trial["packages"][second].get("inTruck", False),
            trial["packages"][first].get("inTruck", False),
        )
        if isvalid(trial):
            return trial

    elif operation == "rotate":
        package_index = rng.randrange(package_count)
        trial = deepcopy(mutated)
        current_orientation = trial["packages"][package_index]["orientation"]
        trial["packages"][package_index]["orientation"] = rng.choice(
            ROTATION_NEIGHBORS[current_orientation]
        )
        if isvalid(trial):
            return trial

    return mutated


def next_generation(population: list[dict], rng: Random) -> list[dict]:
    ordered_population = sorted(population, key=fitness, reverse=True)
    next_population = [deepcopy(ordered_population[0])]

    while len(next_population) < len(population):
        parent_a = selection(population, rng)
        parent_b = selection(population, rng)
        child = crossover(parent_a, parent_b, rng)
        next_population.append(mutate(child, rng))

    return next_population


def solve(
    board: dict,
    population_size: int = 30,
    generations: int = 50,
    seed: int | None = None,
) -> dict:
    if population_size < 1:
        raise ValueError("population_size harus minimal 1")
    if generations < 0:
        raise ValueError("generations tidak boleh negatif")

    rng = Random(seed)
    started_at = perf_counter()
    population = [create_random_individual(board, rng) for _ in range(population_size)]
    initial_scores = [fitness(individual) for individual in population]
    initial_best = deepcopy(max(population, key=fitness))
    history: list[dict] = []
    generation_stats = [
        {
            "generation": 0,
            "maxScore": fitness(initial_best),
            "averageScore": sum(initial_scores) / len(initial_scores),
        }
    ]

    for generation in range(1, generations + 1):
        population = next_generation(population, rng)
        scores = [fitness(individual) for individual in population]
        best_index = max(range(len(population)), key=lambda index: scores[index])
        best_state = deepcopy(population[best_index])
        best_score = scores[best_index]

        history.append(
            {
                "iteration": generation,
                "score": best_score,
                "state": best_state,
            }
        )
        generation_stats.append(
            {
                "generation": generation,
                "maxScore": best_score,
                "averageScore": sum(scores) / len(scores),
            }
        )

    final_best = deepcopy(max(population, key=fitness))

    return {
        "init": initial_best,
        "steps": history,
        "final": final_best,
        "initScore": fitness(initial_best),
        "finalScore": fitness(final_best),
        "iterations": generations,
        "populationSize": population_size,
        "generationStats": generation_stats,
        "durationSeconds": perf_counter() - started_at,
        "seed": seed,
    }
