from pathlib import Path

from plugin.commands.open_git_repo_on_web import Git


def test_find_dot_git_finds_root(tmp_path: Path) -> None:
    dot_git = tmp_path / ".git"
    dot_git.mkdir()
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    result = Git.find_dot_git(nested)
    assert result == tmp_path


def test_find_dot_git_returns_none_outside_repo(tmp_path: Path) -> None:
    # tmp_path has no .git
    result = Git.find_dot_git(tmp_path)
    assert result is None


def test_find_dot_git_on_file(tmp_path: Path) -> None:
    dot_git = tmp_path / ".git"
    dot_git.mkdir()
    f = tmp_path / "file.py"
    f.touch()
    result = Git.find_dot_git(f)
    assert result == tmp_path


def test_is_managed_true(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    assert Git.is_managed(tmp_path) is True


def test_is_managed_false(tmp_path: Path) -> None:
    assert Git.is_managed(tmp_path) is False
