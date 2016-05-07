import sublime
import sublime_plugin
import os

class JumpToFile(sublime_plugin.TextCommand):
    def run(self, edit = None):
        view = self.view
        for region in view.sel():
            if view.score_selector(region.begin(), "parameter.url, string.quoted"):
                # The scope includes the quote characters, so we slice them off
                try_file = view.substr(view.extract_scope(region.begin()))[1:-1]
                view_file = view.file_name()
                if view_file:
                    view_dir = os.path.dirname(view_file)
                    try_file = os.path.join(view_dir, try_file)
                if not os.path.isfile(try_file):
                    try_file += '.rb'
                if os.path.isfile(try_file):
                    view.window().open_file(try_file)
                else:
                    sublime.status_message("Unable to find a file in the current selection")
