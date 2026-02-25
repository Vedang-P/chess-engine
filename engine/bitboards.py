"""Low-level bitboard primitives."""

from __future__ import annotations

MASK_64 = (1 << 64) - 1


def set_bit(bitboard: int, square: int) -> int:
    return bitboard | (1 << square)


def clear_bit(bitboard: int, square: int) -> int:
    return bitboard & ~(1 << square) & MASK_64


def get_bit(bitboard: int, square: int) -> int:
    return (bitboard >> square) & 1


def pop_lsb(bitboard: int) -> tuple[int, int]:
    if bitboard == 0:
        raise ValueError("Cannot pop from empty bitboard")
    lsb = bitboard & -bitboard
    square = lsb.bit_length() - 1
    return square, bitboard ^ lsb


def iter_bits(bitboard: int):
    while bitboard:
        square, bitboard = pop_lsb(bitboard)
        yield square
