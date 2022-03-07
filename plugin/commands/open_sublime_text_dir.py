from functools import lru_cache
from pathlib import Path
from typing import Dict
import sublime
import sublime_plugin
import tempfile

PACKAGE_NAME = __package__.partition(".")[0]


@lru_cache
def get_folder_map() -> Dict[str, str]:
    cache_path = Path(sublime.cache_path())
    packages_path = Path(sublime.packages_path())

    return {
        name: str(path.resolve())
        for name, path in {
            # from OS
            "home": Path.home(),
            "temp_dir": Path(tempfile.gettempdir()),
            # from ST itself
            "bin": Path(sublime.executable_path()).parent,
            "cache": cache_path,
            "data": packages_path / "..",
            "index": cache_path / ".." / "Index",
            "installed_packages": Path(sublime.installed_packages_path()),
            "lib": packages_path / ".." / "Lib",
            "local": packages_path / ".." / "Local",
            "log": packages_path / ".." / "Log",
            "packages": packages_path,
            # from LSP
            "package_storage": cache_path / ".." / "Package Storage",
        }.items()
    }


class OpenSublimeTextDirCommand(sublime_plugin.ApplicationCommand):
    def run(self, folder: str, error_on_not_found: bool = True) -> None:
        window = sublime.active_window()
        path = Path(
            sublime.expand_variables(
                folder,
                {
                    **window.extract_variables(),  # type: ignore
                    **get_folder_map(),
                },
            )
        )

        if not path.is_dir():
            if error_on_not_found:
                sublime.error_message(f"[{PACKAGE_NAME}] Directory not found: `{path}`")
            return

        window.run_command("open_dir", {"dir": str(path)})
