# from https://github.com/sublimehq/sublime_text/issues/299#issuecomment-757427207
import sublime
import sublime_plugin


class ClearConsoleCommand(sublime_plugin.ApplicationCommand):
    def run(self) -> None:
        settings = sublime.load_settings("Preferences.sublime-settings")
        current: int = settings.get("console_max_history_lines")
        settings.set("console_max_history_lines", 1)
        print("")
        settings.set("console_max_history_lines", current)
