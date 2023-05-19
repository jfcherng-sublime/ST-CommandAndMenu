# from https://github.com/sublimehq/sublime_text/issues/299#issuecomment-757427207

from __future__ import annotations

import sublime
import sublime_plugin

ST_SETTING_CONSOLE_MAX_HISTORY_LINES = "console_max_history_lines"


class ClearConsoleCommand(sublime_plugin.ApplicationCommand):
    def run(self) -> None:
        settings = sublime.load_settings("Preferences.sublime-settings")
        current: int = settings.get(ST_SETTING_CONSOLE_MAX_HISTORY_LINES)
        settings.set(ST_SETTING_CONSOLE_MAX_HISTORY_LINES, 1)
        print("")
        settings.set(ST_SETTING_CONSOLE_MAX_HISTORY_LINES, current)
