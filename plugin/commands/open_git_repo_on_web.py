from pathlib import Path
from typing import Optional, Tuple, Union
import re
import shlex
import shutil
import sublime
import sublime_plugin
import subprocess


class GitException(Exception):
    """Exception raised when something went wrong for git"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class Git:
    """Git command wrapper"""

    def __init__(
        self,
        repo_path: Union[str, Path],
        git_bin: str = "git",
        encoding: str = "utf-8",
    ) -> None:
        """Init a Git wrapper with an instance"""

        # always use folder as repo path
        if (path := Path(repo_path)).is_file():
            path = path.parent

        self.repo_path = path
        self.git_bin = shutil.which(git_bin) or git_bin
        self.encoding = encoding

    def run(self, *args: str, timeout_s: float = 3) -> str:
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
            startupinfo=startupinfo,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )

        out, err = process.communicate(timeout=timeout_s)
        ret_code = process.poll() or 0

        if ret_code:
            cmd_str = " ".join(shlex.quote(part) for part in cmd_tuple)
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
                remote = re.sub(r"^refs/remotes/", "", upstream).split("/", 2)[0]

            remote_uri = self.run("remote", "get-url", remote)
            remote_url = self.get_url_from_remote_uri(remote_uri)

            return remote_url
        except GitException:
            return None

    @staticmethod
    def is_in_git_repo(path: Union[str, Path]) -> bool:
        path_prev, path = None, Path(path).resolve()
        while path != path_prev:
            # git dir or worktree, which has a .git file in it
            if (path / ".git").exists():
                return True
            path_prev, path = path, path.parent
        return False

    @staticmethod
    def get_url_from_remote_uri(uri: str) -> Optional[str]:
        url = None

        # SSH (unsupported)
        if re.search(r"^ssh://", uri, re.IGNORECASE):
            url = None

        # HTTP
        if re.search(r"^https?://", uri, re.IGNORECASE):
            url = uri

        # common providers
        if re.search(r"git@", uri, re.IGNORECASE):
            parts = uri[4:].split(":")  # "4:" removes "git@"
            host = ":".join(parts[:-1])
            path = parts[-1]
            url = f"https://{host}/{path}"

        return re.sub(r"\.git$", "", url, re.IGNORECASE) if url else None


def make_git() -> Optional[Git]:
    window = sublime.active_window()
    view = window.active_view()
    path = (view.file_name() or "") if view else ""

    if not path:
        path = (window.folders() or [""])[0]

    return Git(path) if path else None


class OpenGitRepoOnWebCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return git.is_in_git_repo(git.repo_path) if (git := make_git()) else False

    def run(self, remote: Optional[str] = None) -> None:
        if not (git := make_git()):
            return

        if not (repo_url := git.get_remote_web_url(remote=remote)):
            return sublime.error_message("Can't determine repo web URL...")

        sublime.run_command("open_url", {"url": repo_url})
