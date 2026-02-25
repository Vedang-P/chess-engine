"""WebSocket routes for live search telemetry."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from engine.board import Board
from engine.constants import START_FEN
from engine.search import SearchEngine, SearchResult

router = APIRouter()


def _serialize_iteration(result: SearchResult) -> dict:
    return {
        "type": "iteration",
        "depth": result.depth,
        "score": result.score,
        "nodes": result.nodes,
        "nps": result.nps,
        "elapsed_ms": round(result.elapsed_ms, 2),
        "pv": [move.uci() for move in result.pv],
        "candidates": [{"move": c.move, "score": c.score} for c in result.candidates[:10]],
        "best_move": result.best_move.uci() if result.best_move else None,
    }


def _serialize_complete(result: SearchResult) -> dict:
    return {
        "type": "complete",
        "depth": result.depth,
        "score": result.score,
        "nodes": result.nodes,
        "nps": result.nps,
        "elapsed_ms": round(result.elapsed_ms, 2),
        "pv": [move.uci() for move in result.pv],
        "best_move": result.best_move.uci() if result.best_move else None,
    }


@router.websocket("/ws/search")
async def search_websocket(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        while True:
            payload = await websocket.receive_json()
            fen = payload.get("fen", START_FEN)
            max_depth = int(payload.get("max_depth", 5))
            time_limit_ms = int(payload.get("time_limit_ms", 3000))

            board = Board(fen)
            engine = SearchEngine()
            event_queue: asyncio.Queue[dict | None] = asyncio.Queue()
            loop = asyncio.get_running_loop()

            def on_iteration(result: SearchResult) -> None:
                loop.call_soon_threadsafe(event_queue.put_nowait, _serialize_iteration(result))

            async def run_search() -> None:
                try:
                    result = await asyncio.to_thread(
                        engine.search,
                        board,
                        max_depth,
                        time_limit_ms,
                        on_iteration,
                    )
                    await event_queue.put(_serialize_complete(result))
                except Exception as exc:  # noqa: BLE001
                    await event_queue.put({"type": "error", "message": str(exc)})
                finally:
                    await event_queue.put(None)

            worker = asyncio.create_task(run_search())

            while True:
                item = await event_queue.get()
                if item is None:
                    break
                await websocket.send_json(item)

            await worker
    except WebSocketDisconnect:
        return
