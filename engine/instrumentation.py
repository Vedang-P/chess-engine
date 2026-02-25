"""Search instrumentation data structures."""

from __future__ import annotations

from dataclasses import dataclass, field

from .search import SearchResult


@dataclass(slots=True)
class SearchSnapshot:
    depth: int
    score: int
    pv: list[str]
    nodes: int
    nps: int
    elapsed_ms: float
    candidates: list[dict[str, int]]


@dataclass(slots=True)
class SearchRecorder:
    snapshots: list[SearchSnapshot] = field(default_factory=list)

    def on_iteration(self, result: SearchResult) -> None:
        self.snapshots.append(
            SearchSnapshot(
                depth=result.depth,
                score=result.score,
                pv=[m.uci() for m in result.pv],
                nodes=result.nodes,
                nps=result.nps,
                elapsed_ms=result.elapsed_ms,
                candidates=[{"move": c.move, "score": c.score} for c in result.candidates[:10]],
            )
        )
