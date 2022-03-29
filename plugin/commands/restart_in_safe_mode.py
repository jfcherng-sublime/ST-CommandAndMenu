from pathlib import Path
from typing import Any, Iterable, Optional, Union
import sublime
import sublime_plugin
import subprocess
import os

AnyPath = Union[str, Path]


def close_application(pid: int, after_close_cmd: Optional[Iterable[AnyPath]] = None, **kwargs: Any) -> None:
    if sublime.platform() == "windows":
        cmd = ["taskkill", "/f", "/pid", str(pid)]
        # do not create a window for the process
        startupinfo = subprocess.STARTUPINFO()  # type: ignore
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore
    else:
        cmd = ["kill", "-9", str(pid)]
        startupinfo = None  # type: ignore

    if after_close_cmd:
        cmd.append("&&")
        cmd.extend(map(str, after_close_cmd))

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
        bin_dir = Path(sublime.executable_path()).parent
        bin_name = "subl.exe" if sublime.platform() == "windows" else "subl"

        # close ST and restart in safe mode
        close_application(
            os.getppid(),  # plugin_host's parent is the Sublime Text process
            after_close_cmd=(bin_dir / bin_name, "--safe-mode"),
        )
