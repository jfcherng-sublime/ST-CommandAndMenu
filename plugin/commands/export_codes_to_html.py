import re
import string
import sublime
import sublime_plugin
import tempfile


class ExportCodesToHtmlCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, open_html: bool = True) -> None:
        if not (html := self._get_html()):
            sublime.error_message("[export_codes_to_html]\nEmpty html output")
            return

        if open_html:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", prefix="st-", suffix=".html", delete=False) as f:
                f.write(html)
                sublime.run_command("open_url", {"url": f"file:///{f.name}"})
        else:
            sublime.set_clipboard(html)

    def _get_html(self) -> str:
        input_regions = (
            tuple(r for r in self.view.sel() if not r.empty())
            if self.view.has_non_empty_selection_region()
            else (sublime.Region(0, self.view.size()),)
        )
        html = self.view.export_to_html(regions=input_regions, minihtml=False, enclosing_tags=True)

        return self._fix_html(html)

    def _fix_html(self, html: str) -> str:
        # find background color (works in most situations...)
        matches = re.search(r"background-color:([^\"';]+)", html, re.IGNORECASE)
        bgcolor = matches.group(1) if matches else "inherit"
        # table can be copied to Word, PowerPoint while keeping the background color
        html = f"<table><tr><td>{html}</td></tr></table>"
        # fixes many pasting issues in Microsoft Word... don't ask me why it works ¯\_(ツ)_/¯
        html = f'<br style="line-height:0">{html}'

        style = f"<style>{self._css(bgcolor)}</style>"
        return f'<html><head><meta charset="utf-8">{style}</head><body>{html}</body></html>'

    def _css(self, bgcolor: str) -> str:
        css = """
        body {
            background-color: ${bgcolor};
            padding: 1rem;
            margin: 0;
        }
        table {
            background-color: ${bgcolor};
        }
        """
        return re.sub(r"\s+", "", string.Template(css).substitute(bgcolor=bgcolor))
