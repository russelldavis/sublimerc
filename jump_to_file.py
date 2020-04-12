import sublime
import sublime_plugin
import os

class JumpToFile(sublime_plugin.TextCommand):
    def _try_open(self, try_file, path=None):
        if path:
            try_file = os.path.join(path, try_file)

        if not os.path.isfile(try_file):
            try_file += '.rb'

        if os.path.isfile(try_file):
            self.view.window().open_file(try_file)
            return True
        else:
            msg = "Not a file: %s" % try_file
            print(msg)
            sublime.status_message(msg)
            return False


    def run(self, edit = None):
        view = self.view
        for region in view.sel():
            if view.score_selector(region.begin(), "parameter.url, string.quoted"):
                # The scope includes the quote characters, so we slice them off
                try_file = view.substr(view.extract_scope(region.begin()))[1:-1]

                if os.path.isabs(try_file):
                    self._try_open(try_file)
                    continue

                folders = view.window().folders()
                if folders:
                    for folder in folders:
                        if self._try_open(try_file, folder):
                            continue

                view_file = view.file_name()
                if view_file:
                    view_dir = os.path.dirname(view_file)
                    self._try_open(try_file, view_dir)
