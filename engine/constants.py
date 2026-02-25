"""Engine-wide constants and square helpers."""

from __future__ import annotations

WHITE = 0
BLACK = 1
BOTH = 2

PIECE_NONE = -1

WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK = range(12)

PIECE_SYMBOLS = {
    WP: "P",
    WN: "N",
    WB: "B",
    WR: "R",
    WQ: "Q",
    WK: "K",
    BP: "p",
    BN: "n",
    BB: "b",
    BR: "r",
    BQ: "q",
    BK: "k",
}

SYMBOL_TO_PIECE = {v: k for k, v in PIECE_SYMBOLS.items()}

WHITE_PIECES = (WP, WN, WB, WR, WQ, WK)
BLACK_PIECES = (BP, BN, BB, BR, BQ, BK)

CASTLE_WHITE_KING = 1
CASTLE_WHITE_QUEEN = 2
CASTLE_BLACK_KING = 4
CASTLE_BLACK_QUEEN = 8

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

FILES = "abcdefgh"
RANKS = "12345678"

SQUARES = [f"{f}{r}" for r in RANKS for f in FILES]
SQUARE_TO_INDEX = {sq: idx for idx, sq in enumerate(SQUARES)}

A1 = SQUARE_TO_INDEX["a1"]
B1 = SQUARE_TO_INDEX["b1"]
C1 = SQUARE_TO_INDEX["c1"]
D1 = SQUARE_TO_INDEX["d1"]
E1 = SQUARE_TO_INDEX["e1"]
F1 = SQUARE_TO_INDEX["f1"]
G1 = SQUARE_TO_INDEX["g1"]
H1 = SQUARE_TO_INDEX["h1"]
A8 = SQUARE_TO_INDEX["a8"]
B8 = SQUARE_TO_INDEX["b8"]
C8 = SQUARE_TO_INDEX["c8"]
D8 = SQUARE_TO_INDEX["d8"]
E8 = SQUARE_TO_INDEX["e8"]
F8 = SQUARE_TO_INDEX["f8"]
G8 = SQUARE_TO_INDEX["g8"]
H8 = SQUARE_TO_INDEX["h8"]


def square_name(index: int) -> str:
    if not 0 <= index < 64:
        raise ValueError(f"Square index out of range: {index}")
    return SQUARES[index]


def square_index(square: str) -> int:
    try:
        return SQUARE_TO_INDEX[square]
    except KeyError as exc:
        raise ValueError(f"Invalid square: {square}") from exc


def opposite(side: int) -> int:
    return side ^ 1
