import sublime
import sublime_plugin

"""
Like the builtin expand_selection (with {to: "line"}), but does not expand
the selection if it already exactly covers line(s).

Useful for commands like Delete Line so you don't delete an additional line
when the selection already covers an exact set of lines.
"""
class FillSelectionToLineCommand(sublime_plugin.TextCommand):
    def run(self, edit = None):
        view = self.view

        sel = view.sel()
        for region in sel:
            if region.empty():
                continue
            end = region.end()
            if view.substr(end - 1) == "\n":
                sel.subtract(sublime.Region(end - 1, end))

        sel = view.sel()
        for region in sel:
            line_region = view.full_line(region)
            sel.add(line_region)
