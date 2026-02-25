#!/usr/bin/env python3
"""Generate lightweight JANUS demo GIFs for README visuals."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "visuals"

W, H = 1100, 640
BOARD_X, BOARD_Y, CELL = 40, 70, 62

COLORS = {
    "bg": "#161616",
    "panel": "#1e1e1e",
    "border": "#2b2b2b",
    "light": "#f0d9b5",
    "dark": "#b58863",
    "text": "#e6e2d8",
    "gold": "#c6a25a",
    "green": "#6f9d4f",
    "red": "#b84f3a",
    "muted": "#9f988d",
}

PIECES = {
    "wP": "P",
    "bP": "P",
    "wN": "N",
    "bN": "N",
    "wK": "K",
    "bK": "K",
}


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for family in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"):
        try:
            return ImageFont.truetype(family, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_TITLE = _font(36)
FONT_BODY = _font(20)
FONT_MONO = _font(18)
FONT_PIECE = _font(24)


def _sq_to_xy(square: str) -> tuple[int, int]:
    file_idx = ord(square[0]) - ord("a")
    rank = int(square[1])
    x = BOARD_X + file_idx * CELL
    y = BOARD_Y + (8 - rank) * CELL
    return x, y


def _base_canvas(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    draw.text((40, 20), title, fill=COLORS["text"], font=FONT_TITLE)
    draw.rounded_rectangle((690, 70, 1050, 560), radius=14, fill=COLORS["panel"], outline=COLORS["border"], width=2)
    return img, draw


def _draw_board(draw: ImageDraw.ImageDraw, pieces: dict[str, str], heat: dict[str, int] | None = None, selected: str | None = None) -> None:
    heat = heat or {}
    for rank in range(8):
        for file_idx in range(8):
            x = BOARD_X + file_idx * CELL
            y = BOARD_Y + rank * CELL
            is_light = (file_idx + rank) % 2 == 0
            draw.rectangle((x, y, x + CELL, y + CELL), fill=COLORS["light"] if is_light else COLORS["dark"])

    for sq, val in heat.items():
        x, y = _sq_to_xy(sq)
        color = "#c56e5d" if val > 0 else "#7d3a3a"
        draw.rectangle((x + 4, y + 4, x + CELL - 4, y + CELL - 4), fill=color)

    if selected:
        x, y = _sq_to_xy(selected)
        draw.rectangle((x + 4, y + 4, x + CELL - 4, y + CELL - 4), outline=COLORS["gold"], width=3)

    for sq, piece in pieces.items():
        x, y = _sq_to_xy(sq)
        side = piece[0]
        fill = "#f8f6f2" if side == "w" else "#1f1f1f"
        outline = "#5c5c5c" if side == "w" else "#d8d3c8"
        cx, cy = x + CELL // 2, y + CELL // 2
        r = CELL // 2 - 8
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=2)
        text = PIECES.get(piece, "?")
        tw = draw.textlength(text, font=FONT_PIECE)
        draw.text((cx - tw / 2, cy - 14), text, fill=outline, font=FONT_PIECE)


def _draw_eval(draw: ImageDraw.ImageDraw, cp: int, thinking: bool = False) -> None:
    draw.text((720, 110), "EVALUATION", fill=COLORS["gold"], font=FONT_BODY)
    draw.text((720, 145), f"Eval (W): {cp:+d} cp", fill=COLORS["text"], font=FONT_MONO)
    draw.rounded_rectangle((720, 185, 1020, 209), radius=12, fill="#0f0f0f", outline=COLORS["border"], width=1)
    fill_w = int((cp + 900) / 1800 * 296)
    fill_w = max(2, min(296, fill_w))
    draw.rounded_rectangle((722, 187, 722 + fill_w, 207), radius=10, fill="#e6e2d8")

    draw.text((720, 248), "SEARCH", fill=COLORS["gold"], font=FONT_BODY)
    draw.text((720, 282), "Depth 5", fill=COLORS["text"], font=FONT_MONO)
    draw.text((820, 282), "Nodes 30k", fill=COLORS["text"], font=FONT_MONO)

    if thinking:
        for i in range(4):
            x = 730 + i * 28
            fill = "#7dbb6a" if i < 3 else "#365930"
            draw.ellipse((x, 330, x + 14, 344), fill=fill)


def _save_gif(path: Path, frames: list[Image.Image], duration_ms: int = 350) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
    )


def make_play_engine_response() -> None:
    base_pieces = {"e2": "wP", "e7": "bP", "g1": "wN", "g8": "bN", "e1": "wK", "e8": "bK"}
    frames: list[Image.Image] = []

    for step in range(8):
        img, draw = _base_canvas("JANUS Demo: Play Move + Engine Response")
        pieces = dict(base_pieces)
        selected = None
        cp = 12
        thinking = False

        if step >= 2:
            pieces.pop("e2")
            pieces["e4"] = "wP"
            selected = "e4"
            cp = 35
            thinking = True
        if step >= 5:
            pieces.pop("e7")
            pieces["e5"] = "bP"
            cp = 18
            thinking = False

        _draw_board(draw, pieces, selected=selected)
        _draw_eval(draw, cp=cp, thinking=thinking)
        draw.text((720, 380), "PV: e7e5 g1f3 b8c6", fill=COLORS["text"], font=FONT_MONO)
        draw.text((720, 420), "Candidates: e7e5  d7d5  g8f6", fill=COLORS["muted"], font=FONT_MONO)
        frames.append(img)

    _save_gif(OUT_DIR / "demo-play-engine.gif", frames, duration_ms=420)


def make_heatmap_toggle() -> None:
    pieces = {"e4": "wP", "d5": "bP", "g1": "wN", "e1": "wK", "e8": "bK", "c6": "bN"}
    heat = {"e4": 5, "d5": -4, "f6": 3, "c6": -2, "e5": 4, "d4": 2}
    frames: list[Image.Image] = []

    for step in range(8):
        img, draw = _base_canvas("JANUS Demo: Heatmap Toggle")
        show_heat = step % 4 < 2
        _draw_board(draw, pieces, heat=heat if show_heat else {})
        _draw_eval(draw, cp=42)
        state = "Heatmap: ON" if show_heat else "Heatmap: OFF"
        draw.text((720, 380), state, fill=COLORS["text"], font=FONT_BODY)
        draw.text((720, 420), "Toggle visual pressure overlay anytime.", fill=COLORS["muted"], font=FONT_MONO)
        frames.append(img)

    _save_gif(OUT_DIR / "demo-heatmap-toggle.gif", frames, duration_ms=380)


def make_dynamic_value() -> None:
    pieces = {"c3": "wN", "e4": "wP", "e1": "wK", "e8": "bK", "f6": "bN"}
    frames: list[Image.Image] = []

    panels = [
        ("Click a piece to inspect.", None, None),
        ("Square: c3  Piece: Knight", "Dynamic: +332 cp", "Base 320  PST +12"),
        ("Square: e4  Piece: Pawn", "Dynamic: +118 cp", "Base 100  PST +18"),
        ("Deselected", None, None),
    ]

    for step in range(8):
        panel = panels[min(step // 2, len(panels) - 1)]
        selected = None
        if step in (2, 3):
            selected = "c3"
        if step in (4, 5):
            selected = "e4"

        img, draw = _base_canvas("JANUS Demo: Dynamic Value Tracking")
        _draw_board(draw, pieces, selected=selected)
        _draw_eval(draw, cp=26)

        draw.text((720, 380), "DYNAMIC VALUE", fill=COLORS["gold"], font=FONT_BODY)
        draw.text((720, 415), panel[0], fill=COLORS["text"], font=FONT_MONO)
        if panel[1]:
            draw.text((720, 448), panel[1], fill=COLORS["text"], font=FONT_MONO)
        if panel[2]:
            draw.text((720, 480), panel[2], fill=COLORS["muted"], font=FONT_MONO)

        frames.append(img)

    _save_gif(OUT_DIR / "demo-dynamic-value.gif", frames, duration_ms=430)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_play_engine_response()
    make_heatmap_toggle()
    make_dynamic_value()
    print(f"wrote demo gifs in {OUT_DIR}")


if __name__ == "__main__":
    main()
