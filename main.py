"""Command-line utilities for the chess engine."""

from __future__ import annotations

import argparse

from engine.board import Board
from engine.constants import START_FEN
from engine.perft import perft, perft_divide
from engine.search import SearchEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chess engine utilities")
    parser.add_argument("--fen", default=START_FEN, help="FEN position")

    subparsers = parser.add_subparsers(dest="command", required=False)

    perft_parser = subparsers.add_parser("perft", help="Run perft")
    perft_parser.add_argument("depth", type=int, help="Perft depth")
    perft_parser.add_argument("--divide", action="store_true", help="Show per-move split")

    search_parser = subparsers.add_parser("search", help="Run iterative deepening search")
    search_parser.add_argument("--depth", type=int, default=5, help="Max search depth")
    search_parser.add_argument("--time", type=int, default=3000, help="Time limit in ms")

    return parser


def run() -> None:
    parser = build_parser()
    args = parser.parse_args()

    board = Board(args.fen)

    if args.command == "perft":
        if args.divide:
            for move, count in perft_divide(board, args.depth).items():
                print(f"{move}: {count}")
        else:
            print(perft(board, args.depth))
        return

    if args.command == "search":
        engine = SearchEngine()
        result = engine.search(board, max_depth=args.depth, time_limit_ms=args.time)
        print(f"bestmove {result.best_move.uci() if result.best_move else '0000'}")
        print(f"depth {result.depth} score {result.score} nodes {result.nodes} nps {result.nps}")
        print("pv", " ".join(m.uci() for m in result.pv))
        return

    print(board)


if __name__ == "__main__":
    run()
