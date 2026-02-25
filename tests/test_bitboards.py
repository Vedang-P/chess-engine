from engine.bitboards import clear_bit, get_bit, pop_lsb, set_bit


def test_set_get_clear_bit() -> None:
    bb = 0
    bb = set_bit(bb, 0)
    bb = set_bit(bb, 63)

    assert get_bit(bb, 0) == 1
    assert get_bit(bb, 63) == 1
    assert get_bit(bb, 10) == 0

    bb = clear_bit(bb, 0)
    assert get_bit(bb, 0) == 0
    assert get_bit(bb, 63) == 1


def test_pop_lsb_order() -> None:
    bb = 0
    for sq in (2, 5, 11):
        bb = set_bit(bb, sq)

    popped = []
    while bb:
        sq, bb = pop_lsb(bb)
        popped.append(sq)

    assert popped == [2, 5, 11]
