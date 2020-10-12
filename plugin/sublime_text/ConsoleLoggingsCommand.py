import sublime
import sublime_plugin

from abc import abstractmethod
from typing import List

ST_VERSION = int(sublime.version())


class AskConsoleLoggingsCommand(sublime_plugin.ApplicationCommand):
    row_separator = "-" * 30
    logging_methods = sorted(filter(lambda method: method.startswith("log_"), dir(sublime)))

    @abstractmethod
    def is_checked(self) -> bool:
        # @todo there is no way to know whether a certain log_*() method is activated or not at this moment
        return False

    @abstractmethod
    def is_visible(self) -> bool:
        return True

    def is_enabled(self) -> bool:
        return self.is_visible()

    def run(self) -> None:
        answer = sublime.yes_no_cancel_dialog(
            "(De-)Activate console logging methods?\n{}{}".format(
                self.row_separator + "\n",
                "\n".join(self.logging_methods) + "\n",
            ),
            "Activate",
            "Deactivate",
        )

        if answer == sublime.DIALOG_CANCEL:
            return

        if answer == sublime.DIALOG_NO:
            self._enable_logging_methods(self.logging_methods, False)

            return

        if answer == sublime.DIALOG_YES:
            self._enable_logging_methods(self.logging_methods, True)

            return

    def _enable_logging_methods(self, methods: List[str], enable: bool = True) -> None:
        for method in methods:
            try:
                getattr(sublime, method)(enable)
                print("{} console logging: {}".format("Activate" if enable else "Deactivate", method))
            except Exception:
                pass


class AskLogBuildSystemsCommand(AskConsoleLoggingsCommand):
    logging_methods = ["log_build_systems"]

    def is_visible(self) -> bool:
        return ST_VERSION >= 3080


class AskLogCommandsCommand(AskConsoleLoggingsCommand):
    logging_methods = ["log_commands"]

    def is_visible(self) -> bool:
        return ST_VERSION >= 3006


class AskLogControlTreeCommand(AskConsoleLoggingsCommand):
    logging_methods = ["log_control_tree"]

    def is_visible(self) -> bool:
        return ST_VERSION >= 4064


class AskLogFpsCommand(AskConsoleLoggingsCommand):
    logging_methods = ["log_fps"]

    def is_visible(self) -> bool:
        return ST_VERSION >= 4075


class AskLogIndexingCommand(AskConsoleLoggingsCommand):
    logging_methods = ["log_indexing"]

    def is_visible(self) -> bool:
        return ST_VERSION >= 3009


class AskLogInputCommand(AskConsoleLoggingsCommand):
    logging_methods = ["log_input"]

    def is_visible(self) -> bool:
        return ST_VERSION >= 3006


class AskLogResultRegexCommand(AskConsoleLoggingsCommand):
    logging_methods = ["log_result_regex"]

    def is_visible(self) -> bool:
        return ST_VERSION >= 3006
