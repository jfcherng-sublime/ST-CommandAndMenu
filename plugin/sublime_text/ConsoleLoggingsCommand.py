import sublime
import sublime_plugin

from abc import ABCMeta
from typing import List

ST_METHODS = set(dir(sublime))
ST_VERSION = int(sublime.version())


class AbstractAskConsoleLoggingsCommand(sublime_plugin.ApplicationCommand, metaclass=ABCMeta):
    row_separator = "-" * 30

    def is_checked(self) -> bool:
        # @todo there is no way to know whether a certain log_*() method is activated or not at this moment
        return False

    def is_enabled(self) -> bool:
        # if there is a usable command
        return any((method in ST_METHODS) for method in self.get_logging_method_names())

    def is_visible(self) -> bool:
        return self.is_enabled()

    def get_logging_method_names(self) -> List[str]:
        """ Gets names of logging methods. """

        return [self.name()[4:]]  # strips the leading "ask_" from the command name

    def run(self) -> None:
        answer = sublime.yes_no_cancel_dialog(
            "(De-)Activate console logging methods?\n{}{}".format(
                self.row_separator + "\n",
                "\n".join(self.get_logging_method_names()) + "\n",
            ),
            "Activate",
            "Deactivate",
        )

        if answer == sublime.DIALOG_CANCEL:
            return

        if answer == sublime.DIALOG_NO:
            return self._enable_logging_methods(self.get_logging_method_names(), False)

        if answer == sublime.DIALOG_YES:
            return self._enable_logging_methods(self.get_logging_method_names(), True)

    def _enable_logging_methods(self, methods: List[str], enable: bool = True) -> None:
        for method in methods:
            try:
                getattr(sublime, method)(enable)
                print("{} console logging: {}".format("Activate" if enable else "Deactivate", method))
            except Exception:
                print(
                    "Something wrong happened during {}: {}".format(
                        "activating" if enable else "deactivating",
                        method,
                    )
                )


class AskLogAllCommand(AbstractAskConsoleLoggingsCommand):
    """ Ask for activating all logging commands. """

    def get_logging_method_names(self) -> List[str]:
        return sorted(filter(lambda method: method.startswith("log_"), dir(sublime)))


class AskLogBuildSystemsCommand(AbstractAskConsoleLoggingsCommand):
    """ Ask for activating sublime.log_build_systems() """

    ...


class AskLogCommandsCommand(AbstractAskConsoleLoggingsCommand):
    """ Ask for activating sublime.log_commands() """

    ...


class AskLogControlTreeCommand(AbstractAskConsoleLoggingsCommand):
    """ Ask for activating sublime.log_control_tree() """

    ...


class AskLogFpsCommand(AbstractAskConsoleLoggingsCommand):
    """ Ask for activating sublime.log_fps() """

    ...


class AskLogIndexingCommand(AbstractAskConsoleLoggingsCommand):
    """ Ask for activating sublime.log_indexing() """

    ...


class AskLogInputCommand(AbstractAskConsoleLoggingsCommand):
    """ Ask for activating sublime.log_input() """

    ...


class AskLogResultRegexCommand(AbstractAskConsoleLoggingsCommand):
    """ Ask for activating sublime.log_result_regex() """

    ...
