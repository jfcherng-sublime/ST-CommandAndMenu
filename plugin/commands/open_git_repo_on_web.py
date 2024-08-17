from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import threading
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable, TypeVar, cast

import sublime
import sublime_plugin
from more_itertools import first, first_true

from ..constants import STARTUPINFO_DEFAULT

_T_AnyCallable = TypeVar("_T_AnyCallable", bound=Callable[..., Any])


class GitError(Exception):
    """General error for git."""


class GitCommandError(GitError):
    """Failed executing a git command."""


class GitNotFoundError(GitError):
    """Failed finding the git binary."""


class Git:
    """Git command wrapper"""

    def __init__(
        self,
        workspace: str | Path,
        *,
        git_bin: str | Path = "git",
        encoding: str = "utf-8",
        timeout_s: float = 3,
    ) -> None:
        self.git_bin = str(git_bin)
        self.workspace = Path(workspace)
        self.encoding = encoding
        self.timeout_s = timeout_s

    @property
    def git_bin(self) -> str:
        return self._git_bin

    @git_bin.setter
    def git_bin(self, value: str | Path) -> None:
        self._git_bin = self._resolve_git_bin(value)

    @property
    def workspace(self) -> Path:
        return self._workspace

    @workspace.setter
    def workspace(self, value: str | Path) -> None:
        self._workspace = self._resolve_workspace(Path(value))

    @property
    def tracking_remote(self) -> str | None:
        try:
            # `upstream` will be something like "refs/remotes/origin/master"
            upstream = self.run("rev-parse", "--symbolic-full-name", "@{upstream}")
            return upstream.split("/", 3)[2]  # e.g, "origin"
        except GitCommandError:
            return None  # detached HEAD or no upstream

    @property
    def version(self) -> tuple[int, int, int] | None:
        try:
            v_str = self.run("version")
        except GitCommandError:
            return None
        if m := re.search(r"(\d+)\.(\d+)\.(\d+)", v_str):
            return tuple(map(int, m.groups()))  # type: ignore
        return None

    @classmethod
    def is_managed(cls, path: str | Path) -> bool:
        """
        Determines if the `path` is git-managed.

        Note: This only tries to find a `.git` path upwardly. It does not check if it's valid.
        """
        return bool(cls.find_dot_git(path))

    @classmethod
    def find_dot_git(cls, path: str | Path) -> Path | None:
        """Finds the `.git` file (for worktree) or directory for the `path`."""
        try:
            path = Path(path).resolve()
            return first_true((path, *path.parents), pred=lambda p: (p / ".git").exists())
        except Exception:
            return None

    def run(self, *args: str) -> str:
        """Runs a git command and gets its stdout. Raises GitCommandError on failure."""
        stdout, stderr, exit_code = self.run_detailed(*args)
        if exit_code != 0:
            cmd_str = " ".join(map(shlex.quote, (self._git_bin,) + args))
            raise GitCommandError(f"`{cmd_str}` exited with code {exit_code}: {stderr}")
        return stdout

    def run_detailed(self, *args: str) -> tuple[str, str, int]:
        """Runs a git command and gets its `(stdout, stderr, exit_code)`."""
        process = subprocess.Popen(
            (self.git_bin, *args),
            cwd=self.workspace,
            encoding=self.encoding,
            startupinfo=STARTUPINFO_DEFAULT,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(timeout=self.timeout_s)
        return (stdout.rstrip(), stderr.rstrip(), process.poll() or 0)

    def get_remote_uri(self, remote: str | None = None) -> str | None:
        if not (remote := remote or self.tracking_remote):
            return None
        try:
            return self.run("remote", "get-url", remote)
        except GitCommandError:
            return None

    def _resolve_git_bin(self, git_bin: str | Path) -> str:
        if not (git_bin_resolved := shutil.which(str(git_bin))):
            raise GitNotFoundError(f"Cannot resolve git binary: {git_bin}")
        return git_bin_resolved

    def _resolve_workspace(self, workspace: Path) -> Path:
        if workspace.is_file():
            workspace = workspace.parent
        return workspace


def _get_git_workspace(window: sublime.Window) -> str | None:
    """Gets the workspace for running git commands."""
    # if there is an active view and the file is on disk, use its containing folder
    if (view := window.active_view()) and (filename := view.file_name()):
        return str(Path(filename).parent)
    # use the first workspace folder
    return first(window.folders(), None)


def _provide_git_dir(failed_return: Any = None) -> Callable[[_T_AnyCallable], _T_AnyCallable]:
    def decorator(func: _T_AnyCallable) -> _T_AnyCallable:
        @wraps(func)
        def wrapped(self: sublime_plugin.WindowCommand, *args: Any, **kwargs: Any) -> Any:
            if not (git_dir := _get_git_workspace(self.window)):
                return failed_return
            return func(self, git_dir, *args, **kwargs)

        return cast(_T_AnyCallable, wrapped)

    return decorator


def get_st_preferences() -> sublime.Settings:
    return sublime.load_settings("Preferences.sublime-settings")


def get_st_preference(key: str, default: Any = None) -> Any:
    return get_st_preferences().get(key, default)


@lru_cache
def find_git_bin() -> str | None:
    sublime_merge_path: str = get_st_preference("sublime_merge_path") or ""
    candidates: list[str | Path] = ["git"]

    # Sublime Merge on Windows has a bundled git
    if os.name == "nt":
        if sublime_merge_path:
            candidates.append(Path(sublime_merge_path) / "Git/cmd/git.exe")
        candidates.extend((
            R"C:\Program Files\Sublime Merge\Git\cmd\git.exe",  # default installation
            Path(sublime.executable_path()) / "../../Sublime Merge/Git/cmd/git.exe",  # neighbor installation
        ))

    return first_true(map(shutil.which, map(str, candidates)))


def remote_uri_to_web_url(uri: str) -> str | None:
    # user-defined rules
    for rule in get_st_preference("repo.remote_to_web_url", []):
        if re.match(rule["search"], uri):
            return re.sub(rule["search"], rule["replace"], uri)

    # HTTP
    if uri.startswith(("http://", "https://")):
        return uri

    # Bitbucket / GitHub / GitLab / ...
    if uri.startswith("git@"):
        # example => git@github.com:jfcherng-sublime/ST-CommandAndMenu.git
        host, _, path = uri[4:].rpartition(":")  # "4:" removes leading "git@"
        return f"https://{host}/{path}"

    return None


class OpenGitRepoOnWebCommand(sublime_plugin.WindowCommand):
    @_provide_git_dir(failed_return=False)
    def is_enabled(self, git_dir: str) -> bool:  # type: ignore
        return Git.is_managed(git_dir)

    @_provide_git_dir()
    def run(self, git_dir: str, remote: str | None = None) -> None:
        t = threading.Thread(target=self._worker, args=(git_dir, remote))
        t.start()

    @staticmethod
    def _worker(git_dir: str, remote: str | None = None) -> None:
        if not (git_bin := find_git_bin()):
            sublime.error_message("Can't find git binary...")
            return
        git = Git(git_dir, git_bin=git_bin)

        if not (remote_uri := git.get_remote_uri(remote)):
            sublime.error_message(f"Can't determine repo remote URI: {remote}")
            return

        if not (web_url := remote_uri_to_web_url(remote_uri)):
            sublime.error_message(f"Can't convert remote URI to web URL: {remote_uri}")
            return

        sublime.run_command("open_url", {"url": web_url})
