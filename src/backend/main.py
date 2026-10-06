import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from copy import deepcopy

from algo.naikgunung import solve

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:6767"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_board() -> dict:
    board_path = Path(__file__).with_name("board.json")
    return json.loads(board_path.read_text(encoding="utf-8"))

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/api/board")
def get_board() -> dict:
    return load_board()

@app.post("/api/solve")
def run_solver() -> dict:
    board = load_board()
    return solve(board)
