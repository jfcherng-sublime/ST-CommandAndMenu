from __future__ import annotations

import re
import shlex
import shutil
import subprocess
import threading
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar, cast

import sublime
import sublime_plugin

T_Callable = TypeVar("T_Callable", bound=Callable[..., Any])


class GitException(Exception):
    """Exception raised when something went wrong for git"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class Git:
    """Git command wrapper"""

    def __init__(
        self,
        repo_path: str | Path,
        git_bin: str = "git",
        encoding: str = "utf-8",
        shell: bool = False,
        timeout_s: float = 3,
    ) -> None:
        """Init a Git wrapper with an instance"""

        # always use folder as repo path
        if (path := Path(repo_path).resolve()).is_file():
            path = path.parent

        self.repo_path = path
        self.git_bin = shutil.which(git_bin) or git_bin
        self.encoding = encoding
        self.shell = shell
        self.timeout_s = timeout_s

    def run(self, *args: str) -> str:
        """Run a git command."""

        cmd_tuple = (self.git_bin,) + args

        if sublime.platform() == "windows":
            # do not create a window for the process
            startupinfo = subprocess.STARTUPINFO()  # type: ignore
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore
        else:
            startupinfo = None  # type: ignore

        process = subprocess.Popen(
            cmd_tuple,
            cwd=self.repo_path,
            encoding=self.encoding,
            shell=self.shell,
            startupinfo=startupinfo,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )

        out, err = process.communicate(timeout=self.timeout_s)
        ret_code = process.poll() or 0

        if ret_code:
            cmd_str = " ".join(map(shlex.quote, cmd_tuple))
            raise GitException(f"`{cmd_str}` returned code {ret_code}: {err}")

        return out.rstrip()

    def get_version(self) -> tuple[int, int, int] | None:
        try:
            m = re.search(r"(\d+)\.(\d+)\.(\d+)", self.run("version"))
            return tuple(map(int, m.groups())) if m else None  # type: ignore
        except GitException:
            return None

    def get_remote_web_url(self, remote: str | None = None) -> str | None:
        try:
            # use the tracking upstream
            if not remote:
                # `upstream` will be something like "refs/remotes/origin/master"
                upstream = self.run("rev-parse", "--symbolic-full-name", "@{upstream}")
                remote = upstream.split("/", 3)[2]

            return self.get_url_from_remote_uri(self.run("remote", "get-url", remote))
        except GitException:
            return None

    @staticmethod
    def is_in_git_repo(path: str | Path) -> bool:
        path_prev, path = None, Path(path).resolve()
        while path != path_prev:
            # git dir or worktree, which has a .git file in it
            if (path / ".git").exists():
                return True
            path_prev, path = path, path.parent
        return False

    @staticmethod
    def get_url_from_remote_uri(uri: str) -> str | None:
        def remove_trailing_dot_git(s: str) -> str:
            return s[:-4] if s.endswith(".git") else s

        # user-defined rules
        preferences = sublime.load_settings("Preferences.sublime-settings")
        for rule in preferences.get("repo.remote_to_web_url", []):
            if re.match(rule["search"], uri):
                return re.sub(rule["search"], rule["replace"], uri)

        # HTTP
        if uri.startswith(("http://", "https://")):
            return remove_trailing_dot_git(uri)

        # GitHub
        if uri.startswith("git@"):
            # example => git@github.com:jfcherng-sublime/ST-CommandAndMenu.git
            host, _, path = uri[4:].rpartition(":")  # "4:" removes "git@"
            return remove_trailing_dot_git(f"https://{host}/{path}")

        return None


def _get_dir_for_git(view: sublime.View) -> str | None:
    if filename := view.file_name():
        return str(Path(filename).parent)

    if not (window := view.window()):
        return None

    return next(iter(window.folders()), None)


def _provide_git_dir(failed_return: Any = None) -> Callable[[T_Callable], T_Callable]:
    def decorator(func: T_Callable) -> T_Callable:
        @wraps(func)
        def wrapped(self: sublime_plugin.WindowCommand, *args: Any, **kwargs: Any) -> Any:
            if not ((view := self.window.active_view()) and (git_dir := _get_dir_for_git(view))):
                return failed_return
            return func(self, git_dir, *args, **kwargs)

        return cast(T_Callable, wrapped)

    return decorator


class OpenGitRepoOnWebCommand(sublime_plugin.WindowCommand):
    @_provide_git_dir(failed_return=False)
    def is_enabled(self, git_dir: str) -> bool:  # type: ignore
        return Git.is_in_git_repo(git_dir)

    @_provide_git_dir()
    def run(self, git_dir: str, remote: str | None = None) -> None:
        t = threading.Thread(target=self._worker, args=(git_dir, remote))
        t.start()

    @staticmethod
    def _worker(git_dir: str, remote: str | None = None) -> None:
        if not (repo_url := Git(git_dir).get_remote_web_url(remote=remote)):
            sublime.error_message("Can't determine repo web URL...")
            return

        sublime.run_command("open_url", {"url": repo_url})
