# import all listeners and commands
from .commands.clear_console import ClearConsoleCommand
from .commands.console_loggings import ToggleLogBuildSystemsCommand
from .commands.console_loggings import ToggleLogCommandsCommand
from .commands.console_loggings import ToggleLogControlTreeCommand
from .commands.console_loggings import ToggleLogFpsCommand
from .commands.console_loggings import ToggleLogIndexingCommand
from .commands.console_loggings import ToggleLogInputCommand
from .commands.console_loggings import ToggleLogResultRegexCommand
from .commands.open_git_repo_on_web import OpenGitRepoOnWebCommand
from .commands.open_sublime_text_dir import OpenSublimeTextDirCommand
from .commands.safe_mode import SafeModeCommand

__all__ = (
    # ST: core
    "plugin_loaded",
    "plugin_unloaded",
    # ST: commands
    "ClearConsoleCommand",
    "OpenGitRepoOnWebCommand",
    "OpenSublimeTextDirCommand",
    "SafeModeCommand",
    "ToggleLogBuildSystemsCommand",
    "ToggleLogCommandsCommand",
    "ToggleLogControlTreeCommand",
    "ToggleLogFpsCommand",
    "ToggleLogIndexingCommand",
    "ToggleLogInputCommand",
    "ToggleLogResultRegexCommand",
)


def plugin_loaded() -> None:
    pass


def plugin_unloaded() -> None:
    pass
