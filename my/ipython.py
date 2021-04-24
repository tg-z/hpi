"""
Get IPython (REPL) History with datetimes
https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.history.html?highlight=hist#IPython.core.history.HistoryAccessor.__init__

In order to save python history with timestamps, I define the following in my zshrc:

# if I type python with out any arguments, launch ipython instead
python() { python3 "$@" }
python3() {
  if (( $# == 0 )); then
    echo -e "$(tput setaf 2)Launching ipython instead...$(tput sgr0)"
    ipython
  else
    /usr/bin/python3 "$@"
  fi
}
"""

REQUIRES = ["ipython"]


# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import ipython as user_config  # type: ignore[attr-defined]

from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path[s]/glob to the exported ipython sqlite databases
    export_path: Paths


from pathlib import Path
from datetime import datetime
from typing import Iterable, NamedTuple, Iterator
from itertools import chain

from IPython.core.history import HistoryAccessor  # type: ignore[import]

from my.core import get_files, warn_if_empty, Stats, Res
from .utils.common import InputSource


class Command(NamedTuple):
    dt: datetime
    command: str


Results = Iterator[Res[Command]]


# Return backed up sqlite databases
def inputs() -> Iterable[Path]:
    yield from get_files(config.export_path)


def _live_history() -> Results:
    # the empty string makes IPython use the live history file ~/.local/share/ipython/.../history.sqlite
    # instead of one of the files from the export backup
    # merge histories combines those
    #
    # seems that this has the possibility to fail to locate your live
    # history file if its being run in the background? unsure why
    try:
        yield from _parse_database("")
    except Exception as e:
        yield e


def history(from_paths: InputSource = inputs) -> Results:
    yield from _merge_histories(
        *(_parse_database(str(p)) for p in from_paths()), _live_history()
    )


@warn_if_empty
def _merge_histories(*sources: Results) -> Results:
    emitted = set()
    for e in chain(*sources):
        if isinstance(e, Exception):
            yield e
        else:
            key = (e.command, e.dt)
            if key in emitted:
                continue
            emitted.add(key)
            yield e


def _parse_database(sqlite_database: str) -> Results:
    hist = HistoryAccessor(hist_file=sqlite_database)
    total_sessions = hist.get_last_session_id()
    for sess in range(1, total_sessions):
        # get when this session started, use that as timestamp
        session_info = hist.get_session_info(sess)
        assert len(session_info) == 5  # sanity checks
        start_time = session_info[1]
        assert isinstance(start_time, datetime)
        for msg in hist.get_range(sess).fetchall():  # sqlite cursor
            assert len(msg) == 3
            assert isinstance(msg[-1], str)
            yield Command(command=msg[-1], dt=start_time)


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
