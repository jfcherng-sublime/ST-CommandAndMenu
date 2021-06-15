from .plugin import set_up
from .plugin import tear_down

# main plugin classes
from .plugin.ConsoleLoggingsCommand import *
from .plugin.OpenGitRepoOnWebCommand import *
from .plugin.OpenSublimeTextDirCommand import *


def plugin_loaded() -> None:
    set_up()


def plugin_unloaded() -> None:
    tear_down()
