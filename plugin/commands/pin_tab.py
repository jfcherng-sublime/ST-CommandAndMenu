from __future__ import annotations

import sublime
import sublime_plugin

VIEW_SETTING_IS_PINNED = "is_pinned"


def _is_view_pinned(view: sublime.View) -> bool:
    return bool(view.settings().get(VIEW_SETTING_IS_PINNED))


def _pin_view(view: sublime.View) -> None:
    if _is_view_pinned(view):
        return

    view.settings().set(VIEW_SETTING_IS_PINNED, True)
    view.set_status(VIEW_SETTING_IS_PINNED, "📌")


def _unpin_view(view: sublime.View) -> None:
    if not _is_view_pinned(view):
        return

    view.settings().erase(VIEW_SETTING_IS_PINNED)
    view.erase_status(VIEW_SETTING_IS_PINNED)


class PinTabCommand(sublime_plugin.WindowCommand):
    def is_visible(self, group: int, index: int) -> bool:  # type: ignore
        return not _is_view_pinned(self.window.views_in_group(group)[index])

    def run(self, group: int, index: int) -> None:
        _pin_view(self.window.views_in_group(group)[index])


class UnpinTabCommand(sublime_plugin.WindowCommand):
    def is_visible(self, group: int, index: int) -> bool:  # type: ignore
        return _is_view_pinned(self.window.views_in_group(group)[index])

    def run(self, group: int, index: int) -> None:
        _unpin_view(self.window.views_in_group(group)[index])


class CloseUnpinnedTabsCommand(sublime_plugin.WindowCommand):
    def run(self, ask: bool = True) -> None:
        if ask and not sublime.ok_cancel_dialog("Close all unpinned tabs?"):
            return

        for view in self.window.views(include_transient=True):
            if not _is_view_pinned(view):
                view.close()
