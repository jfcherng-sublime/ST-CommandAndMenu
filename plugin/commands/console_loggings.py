from abc import ABC
from typing import Callable, Optional

import sublime
import sublime_plugin


class AbstractToggleConsoleLoggingCommand(sublime_plugin.ApplicationCommand, ABC):
    @property
    def logging_method_name(self) -> str:
        # strips the leading "toggle_" from the command name
        return self.name()[7:]

    @property
    def logging_method(self) -> Callable[..., None]:
        return getattr(sublime, self.logging_method_name)

    @property
    def logging_status_method(self) -> Callable[[], bool]:
        return getattr(sublime, f"get_{self.logging_method_name}")

    def description(self) -> str:
        # "toogle_log_fps" => "Toggle log fps"
        return self.name().replace("_", " ").capitalize()

    def is_checked(self) -> bool:
        return (self.logging_status_method)()

    def is_enabled(self) -> bool:
        try:
            return bool(self.logging_method and self.logging_status_method)
        except AttributeError:
            return False

    is_visible = is_enabled

    def run(self, enable: Optional[bool] = None) -> None:
        args = tuple() if enable is None else (enable,)
        self.logging_method(*args)


class ToggleLogBuildSystemsCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_build_systems()`."""

    pass


class ToggleLogCommandsCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_commands()`."""

    pass


class ToggleLogControlTreeCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_control_tree()`."""

    pass


class ToggleLogFpsCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_fps()`."""

    pass


class ToggleLogIndexingCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_indexing()`."""

    pass


class ToggleLogInputCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_input()`."""

    pass


class ToggleLogResultRegexCommand(AbstractToggleConsoleLoggingCommand):
    """Toggle `sublime.log_result_regex()`."""

    pass
