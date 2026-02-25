"""Legal move generation and attack detection."""

from __future__ import annotations

from .bitboards import iter_bits
from .board import Board
from .constants import (
    A1,
    A8,
    B1,
    B8,
    BLACK,
    BLACK_PIECES,
    BB,
    BK,
    BN,
    BP,
    BQ,
    BR,
    CASTLE_BLACK_KING,
    CASTLE_BLACK_QUEEN,
    CASTLE_WHITE_KING,
    CASTLE_WHITE_QUEEN,
    C1,
    C8,
    D1,
    D8,
    E1,
    E8,
    F1,
    F8,
    G1,
    G8,
    H1,
    H8,
    PIECE_NONE,
    WHITE,
    WHITE_PIECES,
    WB,
    WK,
    WN,
    WP,
    WQ,
    WR,
    opposite,
)
from .move import Move


KNIGHT_DELTAS = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))
KING_DELTAS = ((1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1))
BISHOP_DIRS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
ROOK_DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
QUEEN_DIRS = BISHOP_DIRS + ROOK_DIRS


def _in_bounds(file_idx: int, rank_idx: int) -> bool:
    return 0 <= file_idx < 8 and 0 <= rank_idx < 8


def _sq(file_idx: int, rank_idx: int) -> int:
    return rank_idx * 8 + file_idx


def _build_leaper_attacks(deltas: tuple[tuple[int, int], ...]) -> list[int]:
    table = [0] * 64
    for sq_idx in range(64):
        file_idx = sq_idx % 8
        rank_idx = sq_idx // 8
        mask = 0
        for df, dr in deltas:
            nf, nr = file_idx + df, rank_idx + dr
            if _in_bounds(nf, nr):
                mask |= 1 << _sq(nf, nr)
        table[sq_idx] = mask
    return table


def _build_pawn_attacks(side: int) -> list[int]:
    table = [0] * 64
    for sq_idx in range(64):
        file_idx = sq_idx % 8
        rank_idx = sq_idx // 8
        mask = 0
        if side == WHITE:
            for df in (-1, 1):
                nf, nr = file_idx + df, rank_idx + 1
                if _in_bounds(nf, nr):
                    mask |= 1 << _sq(nf, nr)
        else:
            for df in (-1, 1):
                nf, nr = file_idx + df, rank_idx - 1
                if _in_bounds(nf, nr):
                    mask |= 1 << _sq(nf, nr)
        table[sq_idx] = mask
    return table


KNIGHT_ATTACKS = _build_leaper_attacks(KNIGHT_DELTAS)
KING_ATTACKS = _build_leaper_attacks(KING_DELTAS)
PAWN_ATTACKS = {
    WHITE: _build_pawn_attacks(WHITE),
    BLACK: _build_pawn_attacks(BLACK),
}


def king_square(board: Board, side: int) -> int:
    king_bb = board.piece_bitboards[WK if side == WHITE else BK]
    if king_bb == 0:
        return -1
    return (king_bb & -king_bb).bit_length() - 1


def is_square_attacked(board: Board, square: int, by_side: int) -> bool:
    if by_side == WHITE:
        if board.piece_bitboards[WP] & PAWN_ATTACKS[BLACK][square]:
            return True
        knight_bb = board.piece_bitboards[WN]
        bishop_queen_bb = board.piece_bitboards[WB] | board.piece_bitboards[WQ]
        rook_queen_bb = board.piece_bitboards[WR] | board.piece_bitboards[WQ]
        king_bb = board.piece_bitboards[WK]
    else:
        if board.piece_bitboards[BP] & PAWN_ATTACKS[WHITE][square]:
            return True
        knight_bb = board.piece_bitboards[BN]
        bishop_queen_bb = board.piece_bitboards[BB] | board.piece_bitboards[BQ]
        rook_queen_bb = board.piece_bitboards[BR] | board.piece_bitboards[BQ]
        king_bb = board.piece_bitboards[BK]

    if KNIGHT_ATTACKS[square] & knight_bb:
        return True
    if KING_ATTACKS[square] & king_bb:
        return True

    file_idx = square % 8
    rank_idx = square // 8

    for df, dr in BISHOP_DIRS:
        nf, nr = file_idx + df, rank_idx + dr
        while _in_bounds(nf, nr):
            target_sq = _sq(nf, nr)
            piece = board.piece_on(target_sq)
            if piece != PIECE_NONE:
                if (1 << target_sq) & bishop_queen_bb:
                    return True
                break
            nf += df
            nr += dr

    for df, dr in ROOK_DIRS:
        nf, nr = file_idx + df, rank_idx + dr
        while _in_bounds(nf, nr):
            target_sq = _sq(nf, nr)
            piece = board.piece_on(target_sq)
            if piece != PIECE_NONE:
                if (1 << target_sq) & rook_queen_bb:
                    return True
                break
            nf += df
            nr += dr

    return False


def in_check(board: Board, side: int) -> bool:
    ksq = king_square(board, side)
    if ksq == -1:
        return True
    return is_square_attacked(board, ksq, opposite(side))


def _append_pawn_move(
    moves: list[Move],
    from_sq: int,
    to_sq: int,
    pawn_piece: int,
    captured: int,
    promotion_rank: int,
    is_double_push: bool = False,
    is_en_passant: bool = False,
) -> None:
    target_rank = to_sq // 8
    if target_rank == promotion_rank:
        if pawn_piece == WP:
            promotions = (WQ, WR, WB, WN)
        else:
            promotions = (BQ, BR, BB, BN)
        for promoted in promotions:
            moves.append(
                Move(
                    from_square=from_sq,
                    to_square=to_sq,
                    piece=pawn_piece,
                    captured=captured,
                    promotion=promoted,
                    is_double_push=False,
                    is_en_passant=is_en_passant,
                    is_castle=False,
                )
            )
        return

    moves.append(
        Move(
            from_square=from_sq,
            to_square=to_sq,
            piece=pawn_piece,
            captured=captured,
            promotion=PIECE_NONE,
            is_double_push=is_double_push,
            is_en_passant=is_en_passant,
            is_castle=False,
        )
    )


def _generate_pawn_moves(board: Board, moves: list[Move]) -> None:
    side = board.side_to_move
    if side == WHITE:
        pawns = board.piece_bitboards[WP]
        for sq_idx in iter_bits(pawns):
            file_idx = sq_idx % 8
            rank_idx = sq_idx // 8

            one_up = sq_idx + 8
            if one_up < 64 and board.piece_on(one_up) == PIECE_NONE:
                _append_pawn_move(
                    moves,
                    sq_idx,
                    one_up,
                    WP,
                    PIECE_NONE,
                    promotion_rank=7,
                )
                if rank_idx == 1:
                    two_up = sq_idx + 16
                    if board.piece_on(two_up) == PIECE_NONE:
                        moves.append(
                            Move(
                                from_square=sq_idx,
                                to_square=two_up,
                                piece=WP,
                                is_double_push=True,
                            )
                        )

            if file_idx > 0:
                cap = sq_idx + 7
                if cap < 64:
                    target_piece = board.piece_on(cap)
                    if target_piece in BLACK_PIECES:
                        _append_pawn_move(
                            moves,
                            sq_idx,
                            cap,
                            WP,
                            target_piece,
                            promotion_rank=7,
                        )
                    elif board.en_passant == cap:
                        _append_pawn_move(
                            moves,
                            sq_idx,
                            cap,
                            WP,
                            PIECE_NONE,
                            promotion_rank=7,
                            is_en_passant=True,
                        )

            if file_idx < 7:
                cap = sq_idx + 9
                if cap < 64:
                    target_piece = board.piece_on(cap)
                    if target_piece in BLACK_PIECES:
                        _append_pawn_move(
                            moves,
                            sq_idx,
                            cap,
                            WP,
                            target_piece,
                            promotion_rank=7,
                        )
                    elif board.en_passant == cap:
                        _append_pawn_move(
                            moves,
                            sq_idx,
                            cap,
                            WP,
                            PIECE_NONE,
                            promotion_rank=7,
                            is_en_passant=True,
                        )
    else:
        pawns = board.piece_bitboards[BP]
        for sq_idx in iter_bits(pawns):
            file_idx = sq_idx % 8
            rank_idx = sq_idx // 8

            one_down = sq_idx - 8
            if one_down >= 0 and board.piece_on(one_down) == PIECE_NONE:
                _append_pawn_move(
                    moves,
                    sq_idx,
                    one_down,
                    BP,
                    PIECE_NONE,
                    promotion_rank=0,
                )
                if rank_idx == 6:
                    two_down = sq_idx - 16
                    if board.piece_on(two_down) == PIECE_NONE:
                        moves.append(
                            Move(
                                from_square=sq_idx,
                                to_square=two_down,
                                piece=BP,
                                is_double_push=True,
                            )
                        )

            if file_idx > 0:
                cap = sq_idx - 9
                if cap >= 0:
                    target_piece = board.piece_on(cap)
                    if target_piece in WHITE_PIECES:
                        _append_pawn_move(
                            moves,
                            sq_idx,
                            cap,
                            BP,
                            target_piece,
                            promotion_rank=0,
                        )
                    elif board.en_passant == cap:
                        _append_pawn_move(
                            moves,
                            sq_idx,
                            cap,
                            BP,
                            PIECE_NONE,
                            promotion_rank=0,
                            is_en_passant=True,
                        )

            if file_idx < 7:
                cap = sq_idx - 7
                if cap >= 0:
                    target_piece = board.piece_on(cap)
                    if target_piece in WHITE_PIECES:
                        _append_pawn_move(
                            moves,
                            sq_idx,
                            cap,
                            BP,
                            target_piece,
                            promotion_rank=0,
                        )
                    elif board.en_passant == cap:
                        _append_pawn_move(
                            moves,
                            sq_idx,
                            cap,
                            BP,
                            PIECE_NONE,
                            promotion_rank=0,
                            is_en_passant=True,
                        )


def _generate_leaper_moves(board: Board, moves: list[Move], piece: int, attack_table: list[int]) -> None:
    side = board.side_to_move
    own_occ = board.occupancies[side]
    enemy_set = BLACK_PIECES if side == WHITE else WHITE_PIECES

    for from_sq in iter_bits(board.piece_bitboards[piece]):
        targets = attack_table[from_sq] & ~own_occ
        for to_sq in iter_bits(targets):
            captured = board.piece_on(to_sq)
            if captured != PIECE_NONE and captured not in enemy_set:
                continue
            moves.append(
                Move(
                    from_square=from_sq,
                    to_square=to_sq,
                    piece=piece,
                    captured=captured,
                )
            )


def _generate_slider_moves(board: Board, moves: list[Move], piece: int, directions: tuple[tuple[int, int], ...]) -> None:
    side = board.side_to_move
    own_set = WHITE_PIECES if side == WHITE else BLACK_PIECES

    for from_sq in iter_bits(board.piece_bitboards[piece]):
        file_idx = from_sq % 8
        rank_idx = from_sq // 8

        for df, dr in directions:
            nf, nr = file_idx + df, rank_idx + dr
            while _in_bounds(nf, nr):
                to_sq = _sq(nf, nr)
                captured = board.piece_on(to_sq)
                if captured == PIECE_NONE:
                    moves.append(Move(from_square=from_sq, to_square=to_sq, piece=piece))
                else:
                    if captured not in own_set:
                        moves.append(
                            Move(
                                from_square=from_sq,
                                to_square=to_sq,
                                piece=piece,
                                captured=captured,
                            )
                        )
                    break
                nf += df
                nr += dr


def _generate_castling(board: Board, moves: list[Move]) -> None:
    side = board.side_to_move
    if side == WHITE:
        if board.piece_on(E1) != WK:
            return

        if board.castling_rights & CASTLE_WHITE_KING:
            if (
                board.piece_on(F1) == PIECE_NONE
                and board.piece_on(G1) == PIECE_NONE
                and board.piece_on(H1) == WR
                and not is_square_attacked(board, E1, BLACK)
                and not is_square_attacked(board, F1, BLACK)
                and not is_square_attacked(board, G1, BLACK)
            ):
                moves.append(Move(from_square=E1, to_square=G1, piece=WK, is_castle=True))

        if board.castling_rights & CASTLE_WHITE_QUEEN:
            if (
                board.piece_on(B1) == PIECE_NONE
                and board.piece_on(C1) == PIECE_NONE
                and board.piece_on(D1) == PIECE_NONE
                and board.piece_on(A1) == WR
                and not is_square_attacked(board, E1, BLACK)
                and not is_square_attacked(board, D1, BLACK)
                and not is_square_attacked(board, C1, BLACK)
            ):
                moves.append(Move(from_square=E1, to_square=C1, piece=WK, is_castle=True))
    else:
        if board.piece_on(E8) != BK:
            return

        if board.castling_rights & CASTLE_BLACK_KING:
            if (
                board.piece_on(F8) == PIECE_NONE
                and board.piece_on(G8) == PIECE_NONE
                and board.piece_on(H8) == BR
                and not is_square_attacked(board, E8, WHITE)
                and not is_square_attacked(board, F8, WHITE)
                and not is_square_attacked(board, G8, WHITE)
            ):
                moves.append(Move(from_square=E8, to_square=G8, piece=BK, is_castle=True))

        if board.castling_rights & CASTLE_BLACK_QUEEN:
            if (
                board.piece_on(B8) == PIECE_NONE
                and board.piece_on(C8) == PIECE_NONE
                and board.piece_on(D8) == PIECE_NONE
                and board.piece_on(A8) == BR
                and not is_square_attacked(board, E8, WHITE)
                and not is_square_attacked(board, D8, WHITE)
                and not is_square_attacked(board, C8, WHITE)
            ):
                moves.append(Move(from_square=E8, to_square=C8, piece=BK, is_castle=True))


def generate_pseudo_legal_moves(board: Board) -> list[Move]:
    moves: list[Move] = []
    side = board.side_to_move

    _generate_pawn_moves(board, moves)

    if side == WHITE:
        _generate_leaper_moves(board, moves, WN, KNIGHT_ATTACKS)
        _generate_slider_moves(board, moves, WB, BISHOP_DIRS)
        _generate_slider_moves(board, moves, WR, ROOK_DIRS)
        _generate_slider_moves(board, moves, WQ, QUEEN_DIRS)
        _generate_leaper_moves(board, moves, WK, KING_ATTACKS)
    else:
        _generate_leaper_moves(board, moves, BN, KNIGHT_ATTACKS)
        _generate_slider_moves(board, moves, BB, BISHOP_DIRS)
        _generate_slider_moves(board, moves, BR, ROOK_DIRS)
        _generate_slider_moves(board, moves, BQ, QUEEN_DIRS)
        _generate_leaper_moves(board, moves, BK, KING_ATTACKS)

    _generate_castling(board, moves)
    return moves


def generate_legal_moves(board: Board) -> list[Move]:
    legal_moves: list[Move] = []
    side = board.side_to_move

    for move in generate_pseudo_legal_moves(board):
        if not board.make_move(move):
            continue
        illegal = in_check(board, side)
        board.unmake_move()
        if not illegal:
            legal_moves.append(move)

    return legal_moves
