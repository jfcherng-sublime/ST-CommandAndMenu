from __future__ import annotations

from abc import ABC
from typing import Callable

import sublime
import sublime_plugin


class AbstractToggleConsoleLoggingCommand(sublime_plugin.ApplicationCommand, ABC):
    @property
    def logging_method_name(self) -> str:
        # strips the leading "toggle_" from the command name
        return self.name()[7:]

    @property
    def logging_method(self) -> Callable[..., None] | None:
        return getattr(sublime, self.logging_method_name, None)

    @property
    def logging_status_method(self) -> Callable[[], bool] | None:
        return getattr(sublime, f"get_{self.logging_method_name}", None)

    def description(self) -> str:
        # "toogle_log_fps" => "Toggle log fps"
        return self.name().replace("_", " ").capitalize()

    def is_checked(self) -> bool:
        return (self.logging_status_method)() if self.logging_status_method else False

    def is_enabled(self) -> bool:
        try:
            return bool(self.logging_method and self.logging_status_method)
        except AttributeError:
            return False

    is_visible = is_enabled

    def run(self, enable: bool | None = None) -> None:
        if not self.logging_method:
            return
        args = tuple() if enable is None else (enable,)
        self.logging_method(*args)


class ToggleLogBuildSystemsCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_build_systems()`."""


class ToggleLogCommandsCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_commands()`."""


class ToggleLogControlTreeCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_control_tree()`."""


class ToggleLogFpsCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_fps()`."""


class ToggleLogIndexingCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_indexing()`."""


class ToggleLogInputCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_input()`."""


class ToggleLogResultRegexCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_result_regex()`."""
