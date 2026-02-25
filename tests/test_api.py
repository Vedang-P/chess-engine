"""API smoke tests for production-facing endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.server import app
from engine.constants import START_FEN


client = TestClient(app)


def test_root_and_health() -> None:
    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["status"] == "ok"

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}


def test_legal_moves_contains_position_eval() -> None:
    response = client.post("/legal-moves", json={"fen": START_FEN})
    assert response.status_code == 200
    body = response.json()
    assert "position_eval" in body
    assert "position_eval_cp" in body
    assert isinstance(body["position_eval"], float)
    assert isinstance(body["position_eval_cp"], int)


def test_analyze_contains_position_eval_and_best_move() -> None:
    response = client.post(
        "/analyze",
        json={"fen": START_FEN, "max_depth": 2, "time_limit_ms": 500},
    )
    assert response.status_code == 200
    body = response.json()
    assert "position_eval" in body
    assert "position_eval_cp" in body
    assert body["depth"] >= 1
    assert isinstance(body["best_move"], str) or body["best_move"] is None
