from __future__ import annotations

import os
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import sublime
import sublime_plugin


def _close_application(pid: int, post_close_cmd: Iterable[str | Path] | None = None, **kwargs: Any) -> None:
    if sublime.platform() == "windows":
        cmd = ["taskkill", "/f", "/pid", str(pid)]
        # do not create a window for the process
        startupinfo = subprocess.STARTUPINFO()  # type: ignore
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore
    else:
        cmd = ["kill", "-9", str(pid)]
        startupinfo = None  # type: ignore

    if post_close_cmd:
        cmd.append("&&")
        cmd.extend(map(str, post_close_cmd))

    subprocess.call(cmd, shell=True, startupinfo=startupinfo, **kwargs)


class RestartInSafeModeCommand(sublime_plugin.ApplicationCommand):
    def run(self) -> None:
        if sublime.ok_cancel_dialog(
            "In order to restart in safe mode, the current Sublime Text has to be closed."
            + " Be careful, unsaved changes may lose. Are you sure to continue?"
        ):
            self.go_safe_mode()

    @staticmethod
    def go_safe_mode() -> None:
        _close_application(
            os.getppid(),  # plugin_host's parent is the Sublime Text process
            post_close_cmd=(sublime.executable_path(), "--safe-mode"),
        )
