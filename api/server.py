"""FastAPI server exposing analysis and perft endpoints."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from engine.board import Board
from engine.constants import START_FEN
from engine.perft import perft, perft_divide
from engine.search import SearchEngine

from .websocket import router as websocket_router


class AnalyzeRequest(BaseModel):
    fen: str = Field(default=START_FEN)
    max_depth: int = Field(default=5, ge=1, le=10)
    time_limit_ms: int = Field(default=3000, ge=50, le=120_000)


class PerftRequest(BaseModel):
    fen: str = Field(default=START_FEN)
    depth: int = Field(default=3, ge=1, le=6)
    divide: bool = Field(default=False)


app = FastAPI(title="Chess Engine API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websocket_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    try:
        board = Board(payload.fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    engine = SearchEngine()
    result = engine.search(board, max_depth=payload.max_depth, time_limit_ms=payload.time_limit_ms)

    return {
        "best_move": result.best_move.uci() if result.best_move else None,
        "score": result.score,
        "depth": result.depth,
        "nodes": result.nodes,
        "nps": result.nps,
        "elapsed_ms": round(result.elapsed_ms, 2),
        "pv": [move.uci() for move in result.pv],
        "candidates": [{"move": c.move, "score": c.score} for c in result.candidates[:10]],
    }


@app.post("/perft")
def run_perft(payload: PerftRequest) -> dict:
    try:
        board = Board(payload.fen)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if payload.divide:
        return {"divide": perft_divide(board, payload.depth)}
    return {"nodes": perft(board, payload.depth)}
