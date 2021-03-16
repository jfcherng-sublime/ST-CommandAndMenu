from abc import ABCMeta
from typing import Callable, Optional
import sublime
import sublime_plugin

ST_METHODS = set(dir(sublime))
ST_VERSION = int(sublime.version())


class AbstractToggleConsoleLoggingCommand(sublime_plugin.ApplicationCommand, metaclass=ABCMeta):
    @property
    def logging_method_name(self) -> str:
        # strips the leading "toggle_" from the command name
        return self.name()[7:]

    @property
    def logging_method(self) -> Callable[..., None]:
        return getattr(sublime, self.logging_method_name)

    @property
    def get_logging_method(self) -> Callable[[], bool]:
        return getattr(sublime, f"get_{self.logging_method_name}")

    def is_checked(self) -> bool:
        return (self.get_logging_method)()

    def is_enabled(self) -> bool:
        return self.logging_method_name in ST_METHODS

    def is_visible(self) -> bool:
        return self.is_enabled()

    def run(self, enable: Optional[bool] = None) -> None:
        args = [] if enable is None else [enable]
        self.logging_method(*args)


class ToggleLogBuildSystemsCommand(AbstractToggleConsoleLoggingCommand):
    """ Toggle `sublime.log_build_systems()` """

    ...


class ToggleLogCommandsCommand(AbstractToggleConsoleLoggingCommand):
    """ Toggle `sublime.log_commands()` """

    ...


class ToggleLogControlTreeCommand(AbstractToggleConsoleLoggingCommand):
    """ Toggle `sublime.log_control_tree()` """

    ...


class ToggleLogFpsCommand(AbstractToggleConsoleLoggingCommand):
    """ Toggle `sublime.log_fps()` """

    ...


class ToggleLogIndexingCommand(AbstractToggleConsoleLoggingCommand):
    """ Toggle `sublime.log_indexing()` """

    ...


class ToggleLogInputCommand(AbstractToggleConsoleLoggingCommand):
    """ Toggle `sublime.log_input()` """

    ...


class ToggleLogResultRegexCommand(AbstractToggleConsoleLoggingCommand):
    """ Toggle `sublime.log_result_regex()` """

    ...
