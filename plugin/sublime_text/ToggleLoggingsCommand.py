import sublime
import sublime_plugin


class ToggleLoggingsCommand(sublime_plugin.ApplicationCommand):
    is_logging_enable = False
    loggings = set(filter(lambda method: method.startswith("log_"), dir(sublime)))

    def is_checked(self) -> bool:
        return self.is_logging_enable

    def description(self) -> str:
        return "Toggle all Sublime Text's logging functionalities."

    def run(self, enable=...) -> None:
        self.is_logging_enable = not self.is_logging_enable if enable is ... else bool(enable)

        for logging in self.loggings:
            try:
                getattr(sublime, logging)(self.is_logging_enable)
            except:
                pass

        sublime.message_dialog(
            "Sublime Text loggings: "
            + ("ON" if self.is_logging_enable else "OFF")
            + ("\n" + "-" * 30 + "\n" + "\n".join(self.loggings) if self.is_logging_enable else "")
        )
