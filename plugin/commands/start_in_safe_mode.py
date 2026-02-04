from __future__ import annotations

import subprocess
from typing import override

import sublime
import sublime_plugin

from ..constants import STARTUPINFO_DEFAULT


class StartInSafeModeCommand(sublime_plugin.ApplicationCommand):
    @override
    def run(self, *, close_self: bool = False) -> None:
        self.open_safe_mode(close_self=close_self)

    @staticmethod
    def open_safe_mode(*, close_self: bool = False) -> None:
        subprocess.Popen(
            [sublime.executable_path(), "--safe-mode"],
            shell=True,
            startupinfo=STARTUPINFO_DEFAULT,
        )

        if close_self:
            sublime.run_command("exit")
