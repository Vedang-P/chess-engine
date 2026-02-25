"""Iterative deepening alpha-beta search."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from .board import Board
from .evaluation import evaluate, terminal_score
from .move import Move
from .movegen import generate_legal_moves, in_check


@dataclass(slots=True)
class CandidateScore:
    move: str
    score: int


@dataclass(slots=True)
class SearchResult:
    best_move: Move | None
    score: int
    depth: int
    pv: list[Move]
    nodes: int
    elapsed_ms: float
    nps: int
    candidates: list[CandidateScore]


class _SearchTimeout(Exception):
    pass


class SearchEngine:
    def __init__(self) -> None:
        self.nodes = 0
        self._deadline = 0.0

    def search(
        self,
        board: Board,
        max_depth: int = 5,
        time_limit_ms: int = 3_000,
        on_iteration: Callable[[SearchResult], None] | None = None,
    ) -> SearchResult:
        if max_depth < 1:
            raise ValueError("max_depth must be >= 1")

        self.nodes = 0
        start = perf_counter()
        self._deadline = start + (time_limit_ms / 1000.0)

        best_result = SearchResult(
            best_move=None,
            score=0,
            depth=0,
            pv=[],
            nodes=0,
            elapsed_ms=0.0,
            nps=0,
            candidates=[],
        )

        for depth in range(1, max_depth + 1):
            try:
                score, best_move, pv, candidates = self._search_root(board, depth)
            except _SearchTimeout:
                break

            elapsed_ms = (perf_counter() - start) * 1000.0
            nps = int(self.nodes / max((elapsed_ms / 1000.0), 1e-9))
            best_result = SearchResult(
                best_move=best_move,
                score=score,
                depth=depth,
                pv=pv,
                nodes=self.nodes,
                elapsed_ms=elapsed_ms,
                nps=nps,
                candidates=candidates,
            )
            if on_iteration is not None:
                on_iteration(best_result)

        return best_result

    def _search_root(self, board: Board, depth: int) -> tuple[int, Move | None, list[Move], list[CandidateScore]]:
        self._check_timeout()

        alpha = -100_000
        beta = 100_000

        moves = generate_legal_moves(board)
        if not moves:
            return terminal_score(board, in_check(board, board.side_to_move), 0), None, [], []

        ordered = sorted(moves, key=_move_order_key, reverse=True)

        best_score = -100_000
        best_move: Move | None = None
        best_pv: list[Move] = []
        candidates: list[CandidateScore] = []

        for move in ordered:
            self._check_timeout()
            board.make_move(move)
            child_score, child_pv = self._negamax(board, depth - 1, -beta, -alpha, 1)
            score = -child_score
            board.unmake_move()

            candidates.append(CandidateScore(move=move.uci(), score=score))

            if score > best_score:
                best_score = score
                best_move = move
                best_pv = [move] + child_pv

            if score > alpha:
                alpha = score

        candidates.sort(key=lambda item: item.score, reverse=True)
        return best_score, best_move, best_pv, candidates

    def _negamax(self, board: Board, depth: int, alpha: int, beta: int, ply: int) -> tuple[int, list[Move]]:
        self._check_timeout()
        self.nodes += 1

        if depth == 0:
            return evaluate(board), []

        moves = generate_legal_moves(board)
        if not moves:
            return terminal_score(board, in_check(board, board.side_to_move), ply), []

        best_score = -100_000
        best_line: list[Move] = []

        for move in sorted(moves, key=_move_order_key, reverse=True):
            board.make_move(move)
            child_score, child_line = self._negamax(board, depth - 1, -beta, -alpha, ply + 1)
            score = -child_score
            board.unmake_move()

            if score > best_score:
                best_score = score
                best_line = [move] + child_line

            if score > alpha:
                alpha = score

            if alpha >= beta:
                break

        return best_score, best_line

    def _check_timeout(self) -> None:
        if perf_counter() >= self._deadline:
            raise _SearchTimeout


def _move_order_key(move: Move) -> int:
    score = 0
    if move.captured != -1:
        score += 10_000
    if move.promotion != -1:
        score += 8_000
    if move.is_castle:
        score += 100
    return score
