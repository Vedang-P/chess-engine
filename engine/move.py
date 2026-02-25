"""Move model used by make/unmake."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import PIECE_NONE


@dataclass(frozen=True, slots=True)
class Move:
    from_square: int
    to_square: int
    piece: int
    captured: int = PIECE_NONE
    promotion: int = PIECE_NONE
    is_double_push: bool = False
    is_en_passant: bool = False
    is_castle: bool = False

    def uci(self) -> str:
        from_file = chr(ord("a") + (self.from_square % 8))
        from_rank = str((self.from_square // 8) + 1)
        to_file = chr(ord("a") + (self.to_square % 8))
        to_rank = str((self.to_square // 8) + 1)

        if self.promotion == PIECE_NONE:
            promo = ""
        else:
            promo_map = {
                1: "n",
                2: "b",
                3: "r",
                4: "q",
                7: "n",
                8: "b",
                9: "r",
                10: "q",
            }
            promo = promo_map.get(self.promotion, "")
        return f"{from_file}{from_rank}{to_file}{to_rank}{promo}"

    def __str__(self) -> str:
        return self.uci()
