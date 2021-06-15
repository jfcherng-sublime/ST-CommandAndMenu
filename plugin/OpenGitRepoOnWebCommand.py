from pathlib import Path
from typing import Optional, Tuple
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

    def __init__(self, repo_path: str, git_bin: str = "git", encoding: str = "utf-8") -> None:
        """Init a Git wrapper with an instance"""

        repo_Path = Path(repo_path)

        if repo_Path.is_file():
            repo_Path = repo_Path.parent

        self.repo_path = repo_Path
        self.git_bin = shutil.which(git_bin) or git_bin
        self.encoding = encoding

    def run(self, *args: str, timeout_s: float = 3) -> str:
        """Run a git command."""

        cmd_tuple = (self.git_bin,) + args

        startupinfo = None  # type: Optional[subprocess.STARTUPINFO]
        if sublime.platform() == "windows":
            # do not create a window for the process
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

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
        ret_code = process.poll()

        if ret_code:
            cmd_str = " ".join(shlex.quote(part) for part in cmd_tuple)
            raise GitException(f"`{cmd_str}` returned code {ret_code}: {err}")

        return out.rstrip()

    def get_version(self) -> Optional[Tuple[int, int, int]]:
        try:
            m = re.search(r"(\d+)\.(\d+)\.(\d+)", self.run("version"))

            return tuple(map(lambda x: int(x), m.groups())) if m else None  # type: ignore
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
    def is_in_git_repo(path: Path) -> bool:
        path_prev, path = None, path.resolve()

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


def create_git_object() -> Optional[Git]:
    window = sublime.active_window()
    view = window.active_view()
    path = (view.file_name() or "") if view else ""

    if not path:
        path = (window.folders() or [""])[0]

    return Git(path) if path else None


class OpenGitRepoOnWebCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        git = create_git_object()

        return git.is_in_git_repo(git.repo_path) if git else False

    def run(self, remote: Optional[str] = None) -> None:
        git = create_git_object()
        if not git:
            return

        repo_url = git.get_remote_web_url(remote=remote)
        if not repo_url:
            return sublime.error_message("Can't determine repo web URL...")

        sublime.run_command("open_url", {"url": repo_url})
