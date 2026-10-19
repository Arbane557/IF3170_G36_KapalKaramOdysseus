from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from time import perf_counter

from algo.ga import solve as solve_ga
from algo.naikgunung import (
    solve_random_restart,
    solve_sideways,
    solve_steepest,
    solve_stochastic,
)
from algo.besipanas import solve as solve_sa

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:6767"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/api/solve/hill-climbing/steepest")
def run_steepest(board: dict, max_iter: int = 100) -> dict:
    start = perf_counter()
    result = solve_steepest(board, max_iter)
    result["duration"] = perf_counter() - start
    return result

@app.post("/api/solve/hill-climbing/stochastic")
def run_stochastic(board: dict, max_iter: int = 100) -> dict:
    return solve_stochastic(board, max_iter)

@app.post("/api/solve/hill-climbing/sideways")
def run_sideways(board: dict, max_iter: int = 100, max_sideways: int = 20) -> dict:
    return solve_sideways(board, max_iter, max_sideways)

@app.post("/api/solve/hill-climbing/random-restart")
def run_random_restart(board: dict, max_iter: int = 100, max_restart: int = 10) -> dict:
    return solve_random_restart(board, max_iter, max_restart)

@app.post("/api/solve/simulated-annealing")
def run_simulated_annealing(board: dict, temperature: float = 100, cooling_rate: float = 0.95, max_iter: int = 1000) -> dict:
    return solve_sa(board, temperature, cooling_rate, max_iter)

@app.post("/api/solve/genetic-algorithm")
def run_genetic_algorithm(board: dict, population_size: int = 20, max_iter: int = 100) -> dict:
    return solve_ga(board, population_size, max_iter)
