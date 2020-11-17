import os
import re
import shlex
import shutil
import sublime
import sublime_plugin
import subprocess

from typing import Optional, Tuple


class GitException(Exception):
    """ Exception raised when something went wrong for git """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class Git:
    """ Git command wrapper """

    def __init__(self, repo_path: str, git_bin: str = "git", encoding: str = "utf-8") -> None:
        """ Init a Git wrapper with an instance """

        if os.path.isfile(repo_path):
            repo_path = os.path.dirname(repo_path)

        self.repo_path = repo_path
        self.git_bin = shutil.which(git_bin) or git_bin
        self.encoding = encoding

    def run(self, *args: str, timeout_s: float = 3) -> str:
        """ Run a git command. """

        cmd_tuple = (self.git_bin,) + args

        if os.name == "nt":
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
        ret_code = process.poll()

        if ret_code:
            cmd_str = " ".join(shlex.quote(part) for part in cmd_tuple)
            raise GitException("`{}` returned code {}: {}".format(cmd_str, ret_code, err))

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
    def is_in_git_repo(path: str) -> bool:
        visited = set()

        if path:
            path = os.path.realpath(path)

        while True:
            if not path or path in visited:
                break

            visited.add(path)

            path_test = os.path.join(path, ".git")
            # git dir or worktree
            if os.path.isdir(path_test) or os.path.isfile(path_test):
                return True

            path = os.path.dirname(path)

        return False

    @staticmethod
    def get_url_from_remote_uri(uri: str) -> Optional[str]:
        def strip_dot_git(s: str) -> str:
            return s[:-4] if s.lower().endswith(".git") else s

        uri_lower = uri.lower()

        # SSH (unsupported)
        if uri_lower.startswith("ssh://"):
            return None

        # HTTP
        if uri_lower.startswith("http://") or uri_lower.startswith("https://"):
            return strip_dot_git(uri)

        # common providers
        if uri_lower.startswith("git@"):
            parts = uri.split(":")
            host = ":".join(parts[:-1])
            path = parts[-1]

            return strip_dot_git("https://{}/{}".format(host, path))

        return None


def create_git_object_from_view(view: Optional[sublime.View] = None) -> Optional[Git]:
    if not view:
        view = sublime.active_window().active_view()

        if not view:
            return None

    file_path = view.file_name() or ""

    if not file_path:
        return None

    return Git(file_path)


class OpenGitRepoOnWebCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        git = create_git_object_from_view()

        if not git:
            return False

        return git.is_in_git_repo(git.repo_path)

    def run(self, remote: Optional[str] = None) -> None:  # type: ignore
        git = create_git_object_from_view()

        if not git:
            return

        repo_url = git.get_remote_web_url(remote=remote)
        if not repo_url:
            return sublime.error_message("Can't determine repo web URL...")

        sublime.run_command("open_url", {"url": repo_url})
