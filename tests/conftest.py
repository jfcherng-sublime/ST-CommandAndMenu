"""Mock sublime modules so plugin code can be imported outside Sublime Text."""

import sys
from abc import ABC
from unittest.mock import MagicMock


# sublime_plugin command base classes must be real classes using ABCMeta
# so that subclasses can also mix in ABC without a metaclass conflict.
class _CommandBase(ABC):
    def name(self) -> str:
        return type(self).__name__

    def description(self) -> str:
        return ""

    def is_checked(self) -> bool:
        return False

    def is_enabled(self) -> bool:
        return True

    def is_visible(self) -> bool:
        return True

    def run(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        pass


class _ApplicationCommand(_CommandBase):
    pass


class _WindowCommand(_CommandBase):
    pass


class _TextCommand(_CommandBase):
    pass


sublime_plugin_mock = MagicMock()
sublime_plugin_mock.ApplicationCommand = _ApplicationCommand
sublime_plugin_mock.WindowCommand = _WindowCommand
sublime_plugin_mock.TextCommand = _TextCommand

sublime_mock = MagicMock()
sublime_mock.load_settings.return_value = MagicMock(get=lambda key, default=None: default)

sys.modules.setdefault("sublime", sublime_mock)
sys.modules.setdefault("sublime_plugin", sublime_plugin_mock)
