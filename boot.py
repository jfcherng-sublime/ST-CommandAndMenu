from .plugin import *  # noqa: F401, F403
from .plugin import set_up
from .plugin import tear_down


def plugin_loaded() -> None:
    set_up()


def plugin_unloaded() -> None:
    tear_down()
