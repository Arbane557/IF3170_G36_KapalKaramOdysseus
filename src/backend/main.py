from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from algo.naikgunung import solve

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

@app.post("/api/solve")
def run_solver(board: dict) -> dict:
    return solve(board)
