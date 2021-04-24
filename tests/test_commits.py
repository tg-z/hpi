from pathlib import Path

from my.coding.commits import repos, _cached_commits, Commit

from more_itertools import ilen


def file_count(dir_name: Path) -> int:
    return ilen(dir_name.rglob("*"))


def test():
    all_repos = list(repos())
    assert len(all_repos) > 1
    # get a repo which has lots of files
    # probably has a couple commits
    for r in sorted(all_repos):
        if file_count(r) > 50:
            biggest_repo = r
            break
    else:
        raise RuntimeError("Couldnt find a repo with more than 100 files!")
    commits_for_repo = list(_cached_commits(biggest_repo))
    assert len(commits_for_repo) >= 1
    assert isinstance(commits_for_repo[0], Commit)
