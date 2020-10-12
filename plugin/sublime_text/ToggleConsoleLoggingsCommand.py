import sublime
import sublime_plugin


class ToggleConsoleLoggingsCommand(sublime_plugin.ApplicationCommand):
    logging_methods = sorted(filter(lambda method: method.startswith("log_"), dir(sublime)))

    def description(self) -> str:
        return "Toggle all Sublime Text's logging functionalities."

    def run(self) -> None:
        answer = sublime.yes_no_cancel_dialog("Enable / Disable all console logging methods?", "Enable", "Disable")

        if answer == sublime.DIALOG_CANCEL:
            return

        if answer == sublime.DIALOG_NO:
            self._enable_all_logging_methods(False)
            self._show_result_dialog(False)

            return

        if answer == sublime.DIALOG_YES:
            self._enable_all_logging_methods(True)
            self._show_result_dialog(True)

            return

    def _enable_all_logging_methods(self, enable: bool = True) -> None:
        for method in self.logging_methods:
            try:
                getattr(sublime, method)(enable)
            except Exception:
                pass

    def _show_result_dialog(self, answer: bool) -> None:
        sublime.message_dialog(
            "Console loggings: {}{}{}".format(
                ("enabled" if answer else "disabled") + "\n",
                "-" * 30 + "\n",
                "\n".join(self.logging_methods) + "\n",
            )
        )
