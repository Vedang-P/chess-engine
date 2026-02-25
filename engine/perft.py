"""Perft utilities for move generation correctness checks."""

from __future__ import annotations

from .board import Board
from .movegen import generate_legal_moves


def perft(board: Board, depth: int) -> int:
    if depth < 0:
        raise ValueError("Depth must be >= 0")
    if depth == 0:
        return 1

    moves = generate_legal_moves(board)
    if depth == 1:
        return len(moves)

    nodes = 0
    for move in moves:
        board.make_move(move)
        nodes += perft(board, depth - 1)
        board.unmake_move()
    return nodes


def perft_divide(board: Board, depth: int) -> dict[str, int]:
    if depth < 1:
        raise ValueError("Depth must be >= 1 for perft divide")

    result: dict[str, int] = {}
    for move in generate_legal_moves(board):
        board.make_move(move)
        count = perft(board, depth - 1)
        board.unmake_move()
        result[move.uci()] = count
    return dict(sorted(result.items()))
