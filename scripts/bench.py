#!/usr/bin/env python3
"""Generate reproducible benchmark CSVs for JANUS."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.board import Board
from engine.constants import START_FEN
from engine.perft import perft
from engine.search import SearchEngine


KIWIPETE_FEN = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"


@dataclass(frozen=True)
class PositionCase:
    name: str
    fen: str


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_perft_bench(depths_by_case: dict[PositionCase, list[int]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for case, depths in depths_by_case.items():
        for depth in depths:
            board = Board(case.fen)
            start = perf_counter()
            nodes = perft(board, depth)
            elapsed_ms = (perf_counter() - start) * 1000.0
            nps = int(nodes / max(elapsed_ms / 1000.0, 1e-9))
            rows.append(
                {
                    "position": case.name,
                    "depth": depth,
                    "nodes": nodes,
                    "elapsed_ms": round(elapsed_ms, 3),
                    "nps": nps,
                }
            )
    return rows


def run_search_bench(cases: list[PositionCase], depth_limits: list[int], time_limit_ms: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for case in cases:
        for depth_limit in depth_limits:
            board = Board(case.fen)
            engine = SearchEngine()
            result = engine.search(board, max_depth=depth_limit, time_limit_ms=time_limit_ms)
            rows.append(
                {
                    "position": case.name,
                    "depth_limit": depth_limit,
                    "reached_depth": result.depth,
                    "nodes": result.nodes,
                    "elapsed_ms": round(result.elapsed_ms, 3),
                    "nps": result.nps,
                    "cutoffs": result.cutoffs,
                    "best_move": result.best_move.uci() if result.best_move else "0000",
                    "eval_cp": result.score,
                }
            )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate JANUS benchmark CSV files")
    parser.add_argument(
        "--metrics-dir",
        default=str(ROOT / "docs" / "metrics"),
        help="Output directory for CSV metrics",
    )
    parser.add_argument(
        "--search-time-ms",
        type=int,
        default=4000,
        help="Time limit per search benchmark run in milliseconds",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics_dir = Path(args.metrics_dir)

    perft_cases = [
        PositionCase("start", START_FEN),
        PositionCase("kiwipete", KIWIPETE_FEN),
    ]
    search_cases = [
        PositionCase("start", START_FEN),
        PositionCase("open_after_e4", "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"),
    ]

    perft_rows = run_perft_bench(
        {
            perft_cases[0]: [1, 2, 3, 4],
            # Depth 4 on Kiwipete is very expensive; keep default benchmark snappy.
            perft_cases[1]: [1, 2, 3],
        }
    )
    search_rows = run_search_bench(search_cases, depth_limits=[1, 2, 3, 4, 5], time_limit_ms=args.search_time_ms)

    perft_path = metrics_dir / "perft_metrics.csv"
    search_path = metrics_dir / "search_metrics.csv"

    _write_csv(
        perft_path,
        fieldnames=["position", "depth", "nodes", "elapsed_ms", "nps"],
        rows=perft_rows,
    )
    _write_csv(
        search_path,
        fieldnames=[
            "position",
            "depth_limit",
            "reached_depth",
            "nodes",
            "elapsed_ms",
            "nps",
            "cutoffs",
            "best_move",
            "eval_cp",
        ],
        rows=search_rows,
    )

    print(f"wrote {perft_path}")
    print(f"wrote {search_path}")


if __name__ == "__main__":
    main()
