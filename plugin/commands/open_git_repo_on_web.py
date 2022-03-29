from pathlib import Path
from typing import Any, Callable, Optional, Tuple, TypeVar, Union, cast
import re
import shlex
import shutil
import sublime
import sublime_plugin
import subprocess
import threading

AnyCallable = TypeVar("AnyCallable", bound=Callable[..., Any])
PathLike = Union[str, Path]


class GitException(Exception):
    """Exception raised when something went wrong for git"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class Git:
    """Git command wrapper"""

    def __init__(
        self,
        repo_path: PathLike,
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

    def get_version(self) -> Optional[Tuple[int, int, int]]:
        try:
            m = re.search(r"(\d+)\.(\d+)\.(\d+)", self.run("version"))
            return tuple(map(int, m.groups())) if m else None  # type: ignore
        except GitException:
            return None

    def get_remote_web_url(self, remote: Optional[str] = None) -> Optional[str]:
        try:
            # use the tracking upstream
            if not remote:
                # `upstream` will be something like "refs/remotes/origin/master"
                upstream = self.run("rev-parse", "--symbolic-full-name", "@{upstream}")
                remote = re.sub(r"^refs/remotes/", "", upstream).partition("/")[0]

            remote_uri = self.run("remote", "get-url", remote)
            remote_url = self.get_url_from_remote_uri(remote_uri)

            return remote_url
        except GitException:
            return None

    @staticmethod
    def is_in_git_repo(path: PathLike) -> bool:
        path_prev, path = None, Path(path).resolve()
        while path != path_prev:
            # git dir or worktree, which has a .git file in it
            if (path / ".git").exists():
                return True
            path_prev, path = path, path.parent
        return False

    @staticmethod
    def get_url_from_remote_uri(uri: str) -> Optional[str]:
        url: Optional[str] = None
        re_flags = re.IGNORECASE | re.MULTILINE

        # SSH (unsupported)
        if re.search(r"^ssh://", uri, re_flags):
            url = None

        # HTTP
        if re.search(r"^https?://", uri, re_flags):
            url = uri

        # common providers
        if re.search(r"^git@", uri, re_flags):
            parts = uri[4:].split(":")  # "4:" removes "git@"
            host = ":".join(parts[:-1])
            path = parts[-1]
            url = f"https://{host}/{path}"

        return re.sub(r"\.git$", "", url, re_flags) if url else None


def get_dir_for_git(view: sublime.View) -> Optional[str]:
    if filename := view.file_name():
        return str(Path(filename).parent)

    if not (window := view.window()):
        return None

    return next(iter(window.folders()), None)


def guarantee_git_dir(failed_return: Optional[Any] = None) -> Callable[[AnyCallable], AnyCallable]:
    def decorator(func: AnyCallable) -> AnyCallable:
        def wrapped(self: sublime_plugin.WindowCommand, *args: Any, **kwargs: Any) -> Any:
            if not ((view := self.window.active_view()) and (git_dir := get_dir_for_git(view))):
                return failed_return
            return func(self, git_dir, *args, **kwargs)

        return cast(AnyCallable, wrapped)

    return decorator


class OpenGitRepoOnWebCommand(sublime_plugin.WindowCommand):
    @guarantee_git_dir(failed_return=False)
    def is_enabled(self, git_dir: str) -> bool:  # type: ignore
        return Git.is_in_git_repo(git_dir)

    @guarantee_git_dir()
    def run(self, git_dir: str, remote: Optional[str] = None) -> None:
        t = threading.Thread(target=self._worker, args=(git_dir, remote))
        t.start()

    @staticmethod
    def _worker(git_dir: str, remote: Optional[str] = None) -> None:
        if not (git := Git(git_dir)):
            return

        if not (repo_url := git.get_remote_web_url(remote=remote)):
            return sublime.error_message("Can't determine repo web URL...")

        sublime.run_command("open_url", {"url": repo_url})
