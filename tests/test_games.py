from more_itertools import ilen

from my.blizzard import events
from my.league import history
from my.steam import games, achievements
from my.chess import history as chess_history


def test_blizzard():

    ev = list(events())
    assert len(ev) >= 100


def test_league():

    gs = list(history())
    assert len(gs) > 50
    assert len(gs[0].players) == 10


def test_steam():

    assert ilen(games()) > 10
    ach = list(achievements())
    assert any([a.game_name == "Counter-Strike: Global Offensive" for a in ach])


def test_chess():
    assert ilen(chess_history()) > 10
