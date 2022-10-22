# import all listeners and commands
from .commands.clear_console import ClearConsoleCommand
from .commands.console_loggings import (
    ToggleLogBuildSystemsCommand,
    ToggleLogCommandsCommand,
    ToggleLogControlTreeCommand,
    ToggleLogFpsCommand,
    ToggleLogIndexingCommand,
    ToggleLogInputCommand,
    ToggleLogResultRegexCommand,
)
from .commands.open_git_repo_on_web import OpenGitRepoOnWebCommand
from .commands.open_sublime_text_dir import OpenSublimeTextDirCommand
from .commands.pin_tab import CloseUnpinnedTabsCommand, PinTabCommand, UnpinTabCommand
from .commands.restart_in_safe_mode import RestartInSafeModeCommand

__all__ = (
    # ST: core
    "plugin_loaded",
    "plugin_unloaded",
    # ST: commands
    "ClearConsoleCommand",
    "CloseUnpinnedTabsCommand",
    "OpenGitRepoOnWebCommand",
    "OpenSublimeTextDirCommand",
    "PinTabCommand",
    "RestartInSafeModeCommand",
    "ToggleLogBuildSystemsCommand",
    "ToggleLogCommandsCommand",
    "ToggleLogControlTreeCommand",
    "ToggleLogFpsCommand",
    "ToggleLogIndexingCommand",
    "ToggleLogInputCommand",
    "ToggleLogResultRegexCommand",
    "UnpinTabCommand",
)


def plugin_loaded() -> None:
    pass


def plugin_unloaded() -> None:
    pass
