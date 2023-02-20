import sublime
import sublime_plugin

VIEW_SETTING_IS_PINNED = "is_pinned"


def is_view_pinned(view: sublime.View) -> bool:
    return bool(view.settings().get(VIEW_SETTING_IS_PINNED))


def pin_view(view: sublime.View) -> None:
    view.settings().set(VIEW_SETTING_IS_PINNED, True)
    view.set_status(VIEW_SETTING_IS_PINNED, "📌")


def unpin_view(view: sublime.View) -> None:
    view.settings().erase(VIEW_SETTING_IS_PINNED)
    view.erase_status(VIEW_SETTING_IS_PINNED)


class PinTabCommand(sublime_plugin.WindowCommand):
    def is_visible(self, group: int, index: int) -> bool:  # type: ignore
        return not is_view_pinned(self.window.views_in_group(group)[index])

    def run(self, group: int, index: int) -> None:
        pin_view(self.window.views_in_group(group)[index])


class UnpinTabCommand(sublime_plugin.WindowCommand):
    def is_visible(self, group: int, index: int) -> bool:  # type: ignore
        return is_view_pinned(self.window.views_in_group(group)[index])

    def run(self, group: int, index: int) -> None:
        unpin_view(self.window.views_in_group(group)[index])


class CloseUnpinnedTabsCommand(sublime_plugin.WindowCommand):
    def run(self, ask: bool = True) -> None:
        if ask and not sublime.ok_cancel_dialog("Close all unpinned tabs?"):
            return

        for view in self.window.views(include_transient=True):
            if not is_view_pinned(view):
                view.close()
