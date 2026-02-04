from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from functools import cached_property
from typing import override

import sublime
import sublime_plugin


class AbstractToggleConsoleLoggingCommand(sublime_plugin.ApplicationCommand, ABC):
    @cached_property
    def logger_func_name(self) -> str:
        """The logger function name in the `sublime` module. E.g., `"log_commands"`."""
        return self.name()[7:]  # strips the leading "toggle_" from the command name

    @cached_property
    def logger_status_getter(self) -> Callable[[], bool] | None:
        """The getter function to check the status of the logger. E.g., `sublime.get_log_commands`."""
        return getattr(sublime, f"get_{self.logger_func_name}", None)

    @cached_property
    def logger_status_setter(self) -> Callable[..., None] | None:
        """The setter function to set/toggle the logger status. E.g., `sublime.log_commands`."""
        return getattr(sublime, self.logger_func_name, None)

    @property
    def logger_status(self) -> bool | None:
        """The current status of the logger. `None` if there is no such logger."""
        return self.logger_status_getter() if self.logger_status_getter else None

    @override
    def description(self) -> str:
        # "toogle_log_fps" => "Toggle Log FPS"
        return self.name().replace("_", " ").title().replace("Fps", "FPS")

    @override
    def is_checked(self) -> bool:
        return bool(self.logger_status)

    @override
    def is_enabled(self) -> bool:
        return bool(self.logger_status_getter and self.logger_status_setter)

    is_visible = is_enabled

    @override
    def run(self, enable: bool | None = None) -> None:
        if self.logger_status_setter:
            if enable is None:
                self.logger_status_setter()
            else:
                self.logger_status_setter(enable)


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
