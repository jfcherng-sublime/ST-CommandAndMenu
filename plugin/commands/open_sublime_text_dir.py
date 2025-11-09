from __future__ import annotations

import os
import tempfile
from functools import cached_property
from pathlib import Path

import sublime
import sublime_plugin

assert __package__

PACKAGE_NAME = __package__.partition(".")[0]


class OpenSublimeTextDirCommand(sublime_plugin.ApplicationCommand):
    @cached_property
    def folder_map(self) -> dict[str, str]:
        def _may_resolve_path(path: Path) -> Path:
            try:
                return path.resolve()  # will fail on a Direct-IO disk
            except OSError:
                return path

        cache_path = Path(sublime.cache_path())
        packages_path = Path(sublime.packages_path())
        installed_packages = Path(sublime.installed_packages_path())

        return {
            name: str(_may_resolve_path(path))
            for name, path in (
                # from OS
                ("home", Path.home()),
                ("temp_dir", Path(tempfile.gettempdir())),
                # from ST itself
                ("bin", Path(sublime.executable_path()).parent),
                ("cache", cache_path),
                ("data", packages_path / ".."),
                ("index", cache_path / "../Index"),
                ("installed_packages", installed_packages),
                ("lib", packages_path / "../Lib"),
                ("local", packages_path / "../Local"),
                ("log", packages_path / "../Log"),
                ("packages", packages_path),
                # from LSP
                ("package_storage", cache_path / "../Package Storage"),
            )
        }

    def run(self, folder: str, error_on_not_found: bool = True) -> None:
        window = sublime.active_window()
        path = Path(
            sublime.expand_variables(
                folder,
                os.environ | window.extract_variables() | self.folder_map,
            )
        )

        if not path.is_dir():
            if error_on_not_found:
                sublime.error_message(f"[{PACKAGE_NAME}] Directory not found: `{path}`")
            return

        window.run_command("open_dir", {"dir": str(path)})
