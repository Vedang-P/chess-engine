from engine.board import Board
from engine.movegen import generate_legal_moves


def _moves_uci(board: Board) -> set[str]:
    return {m.uci() for m in generate_legal_moves(board)}


def test_start_position_has_20_legal_moves() -> None:
    board = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    moves = generate_legal_moves(board)
    assert len(moves) == 20


def test_castling_moves_generated_when_legal() -> None:
    board = Board("4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1")
    moves = _moves_uci(board)
    assert "e1g1" in moves
    assert "e1c1" in moves


def test_castling_blocked_if_square_under_attack() -> None:
    board = Board("4kr2/8/8/8/8/8/8/R3K2R w KQ - 0 1")
    moves = _moves_uci(board)
    assert "e1g1" not in moves
    assert "e1c1" in moves


def test_illegal_move_leaving_king_in_check_filtered_out() -> None:
    board = Board("4k3/8/8/8/8/8/4r3/R3K3 w Q - 0 1")
    moves = _moves_uci(board)

    # White is in check from e2 rook: rook move a1a2 is illegal because it ignores check.
    assert "a1a2" not in moves
    # King escape should remain legal.
    assert "e1d1" in moves


def test_en_passant_generated_when_available() -> None:
    board = Board("8/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
    moves = _moves_uci(board)
    assert "e5d6" in moves


def test_promotion_moves_generated() -> None:
    board = Board("k7/4P3/8/8/8/8/8/4K3 w - - 0 1")
    moves = _moves_uci(board)
    assert {"e7e8q", "e7e8r", "e7e8b", "e7e8n"}.issubset(moves)
