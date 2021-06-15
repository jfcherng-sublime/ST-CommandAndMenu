from functools import lru_cache
from pathlib import Path
from typing import Dict
import os
import sublime
import sublime_plugin
import tempfile

PACKAGE_NAME = __package__.split(".")[0]


@lru_cache
def get_folder_map() -> Dict[str, str]:
    return {
        name: str(path.resolve())
        for name, path in {
            # from OS
            "home": Path.home(),
            "temp_dir": Path(tempfile.gettempdir()),
            # from ST itself
            "bin": Path(sublime.executable_path()).parent,
            "cache": Path(sublime.cache_path()),
            "data": Path(sublime.packages_path(), ".."),
            "index": Path(sublime.cache_path()) / ".." / "Index",
            "installed_packages": Path(sublime.installed_packages_path()),
            "lib": Path(sublime.packages_path()) / ".." / "Lib",
            "local": Path(sublime.packages_path()) / ".." / "Local",
            "log": Path(sublime.packages_path()) / ".." / "Log",
            "packages": Path(sublime.packages_path()),
            # from LSP
            "package_storage": Path(sublime.cache_path()) / ".." / "Package Storage",
        }.items()
    }


class OpenSublimeTextDirCommand(sublime_plugin.ApplicationCommand):
    def run(self, folder: str) -> None:
        window = sublime.active_window()
        path = sublime.expand_variables(
            folder,
            {
                **window.extract_variables(),
                **get_folder_map(),
            },
        )

        if not os.path.isdir(path):
            return sublime.error_message(f"[{PACKAGE_NAME}] Directory not found: `{path}`")

        window.run_command("open_dir", {"dir": path})
