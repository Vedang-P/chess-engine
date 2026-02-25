from engine.board import Board
from engine.search import SearchEngine


def test_search_returns_a_legal_move() -> None:
    board = Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")
    engine = SearchEngine()

    result = engine.search(board, max_depth=2, time_limit_ms=2000)

    assert result.best_move is not None
    assert result.depth >= 1
    assert result.nodes > 0
