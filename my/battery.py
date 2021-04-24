"""
Parses a basic logfile of my laptop battery
This logs once per minute, and is part of my menu bar script
https://sean.fish/d/.config/i3blocks/blocks/battery
"""

# see https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py for an example
from my.config import battery as user_config  # type: ignore[attr-defined]
from my.core import Paths, dataclass


@dataclass
class config(user_config):
    # path/glob to the battery logfile
    export_path: Paths


import csv
from typing import Sequence
from pathlib import Path

from my.core import get_files, warn_if_empty, Stats
from my.core.common import listify
from .utils.time import parse_datetime_sec
from .utils.common import InputSource


@listify
def inputs() -> Sequence[Path]:  # type: ignore[misc]
    """Returns all battery log/datafiles"""
    yield from get_files(config.export_path)


from datetime import datetime
from typing import NamedTuple, Iterator, Set, Tuple, List
from itertools import chain


# represents one battery entry, the status at some point
class Entry(NamedTuple):
    dt: datetime
    percentage: int
    status: str


Results = Iterator[Entry]


def history(from_paths: InputSource = inputs) -> Results:
    datafiles: List[Path] = list(from_paths())
    if len(datafiles) == 1:
        yield from _parse_file(datafiles[0])
    else:
        yield from _merge_histories(*map(_parse_file, from_paths()))


@warn_if_empty
def _merge_histories(*sources: Results) -> Results:
    emitted: Set[Tuple[datetime, int]] = set()
    for e in chain(*sources):
        key = (e.dt, e.percentage)
        if key in emitted:
            continue
        yield e
        emitted.add(key)


def _parse_file(histfile: Path) -> Results:
    with histfile.open("r", encoding="utf-8", newline="") as f:
        csv_reader = csv.reader(
            f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        for row in csv_reader:
            yield Entry(
                dt=parse_datetime_sec(row[0]), percentage=int(row[1]), status=row[2]
            )


def stats() -> Stats:
    from my.core import stat

    return {**stat(history)}
