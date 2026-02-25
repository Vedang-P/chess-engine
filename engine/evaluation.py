"""Static board evaluation."""

from __future__ import annotations

from .bitboards import iter_bits
from .board import Board
from .constants import (
    BLACK,
    BB,
    BK,
    BN,
    BP,
    BQ,
    BR,
    WHITE,
    WB,
    WK,
    WN,
    WP,
    WQ,
    WR,
)

# Material values in centipawns.
PIECE_VALUES = {
    WP: 100,
    WN: 320,
    WB: 330,
    WR: 500,
    WQ: 900,
    WK: 0,
    BP: 100,
    BN: 320,
    BB: 330,
    BR: 500,
    BQ: 900,
    BK: 0,
}

# Basic center pressure bonus table shared by both colors (mirrored for black).
CENTER_BONUS = [
    0, 0, 5, 5, 5, 5, 0, 0,
    0, 5, 10, 10, 10, 10, 5, 0,
    5, 10, 15, 20, 20, 15, 10, 5,
    5, 10, 20, 25, 25, 20, 10, 5,
    5, 10, 20, 25, 25, 20, 10, 5,
    5, 10, 15, 20, 20, 15, 10, 5,
    0, 5, 10, 10, 10, 10, 5, 0,
    0, 0, 5, 5, 5, 5, 0, 0,
]


def _mirror_sq(square: int) -> int:
    file_idx = square % 8
    rank_idx = square // 8
    return (7 - rank_idx) * 8 + file_idx


def evaluate(board: Board) -> int:
    """Return score from side-to-move perspective in centipawns."""
    white_score = 0
    black_score = 0

    for piece, bb in enumerate(board.piece_bitboards):
        base = PIECE_VALUES[piece]
        for sq in iter_bits(bb):
            pst = CENTER_BONUS[sq]
            if piece >= BP:
                black_score += base + CENTER_BONUS[_mirror_sq(sq)]
            else:
                white_score += base + pst

    score = white_score - black_score
    return score if board.side_to_move == WHITE else -score


def terminal_score(board: Board, side_to_move_in_check: bool, ply: int) -> int:
    if side_to_move_in_check:
        # Sooner mates score higher.
        return -100_000 + ply
    return 0
