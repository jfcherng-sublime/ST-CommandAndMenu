import os
import sublime
import sublime_plugin

from functools import lru_cache
from typing import Dict


@lru_cache
def get_folder_map() -> Dict[str, str]:
    return {
        k: os.path.realpath(v)
        for k, v in {
            # from ST itself
            "bin": os.path.dirname(sublime.executable_path()),
            "cache": sublime.cache_path(),
            "data": os.path.join(sublime.packages_path(), ".."),
            "index": os.path.join(sublime.cache_path(), "..", "Index"),
            "installed_packages": sublime.installed_packages_path(),
            "lib": os.path.join(sublime.packages_path(), "..", "Lib"),
            "local": os.path.join(sublime.packages_path(), "..", "Local"),
            "log": os.path.join(sublime.packages_path(), "..", "Log"),
            "packages": sublime.packages_path(),
            # from LSP
            "package_storage": os.path.join(sublime.cache_path(), "..", "Package Storage"),
        }.items()
    }


@lru_cache
def get_folder_path(folder: str) -> str:
    m = get_folder_map()

    if folder not in m:
        print(
            "[{}] Wrong folder parameter: `{}`. Valid values are: `{}`",
            __package__,
            folder,
            ", ".join(m.keys()),
        )

        raise ValueError()

    return m[folder]


class OpenSublimeTextDirCommand(sublime_plugin.ApplicationCommand):
    def run(self, folder: str) -> None:  # type: ignore
        path = get_folder_path(folder)

        if not os.path.isdir(path):
            sublime.error_message("Directory not found: `{}`".format(path))

            return

        sublime.active_window().run_command("open_dir", {"dir": path})
