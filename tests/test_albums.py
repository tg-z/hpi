from more_itertools import ilen

from my.albums import to_listen, history


def test_trakt() -> None:
    assert ilen(history()) > 1
    assert ilen(to_listen()) > 1
