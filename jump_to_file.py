import sublime
import sublime_plugin
import os
from os.path import splitext

def _try_open(window, try_file, path=None):
    if path:
        try_file = os.path.join(path, try_file)

    if not os.path.isfile(try_file):
        try_file += '.rb'

    if os.path.isfile(try_file):
        window.open_file(try_file)
        return True
    else:
        return False


class JumpToHeaderOrImpl(sublime_plugin.TextCommand):
    def run(self, edit = None):
        view = self.view
        window = view.window()
        file = view.file_name()
        if file is None:
            return

        base, file_ext = splitext(file)
        impl_exts = [".cc", ".cpp", ".c"]

        if file_ext == ".h":
            for impl_ext in impl_exts:
                if _try_open(window, base + impl_ext):
                    return
        else:
            for impl_ext in impl_exts:
                if file_ext == impl_ext:
                    if _try_open(window, base + ".h"):
                        return


class JumpToFile(sublime_plugin.TextCommand):

    def run(self, edit = None):
        view = self.view
        window = view.window()
        for region in view.sel():
            if view.score_selector(region.begin(), "parameter.url, string.quoted"):
                # The scope includes the quote characters, so we slice them off
                try_file = view.substr(view.extract_scope(region.begin()))[1:-1]

                if os.path.isabs(try_file):
                    _try_open(window, try_file)
                    continue

                folders = view.window().folders()
                if folders:
                    for folder in folders:
                        if _try_open(window, try_file, folder):
                            continue

                view_file = view.file_name()
                if view_file:
                    view_dir = os.path.dirname(view_file)
                    if _try_open(window, try_file, view_dir):
                        continue

                msg = "Not a file: %s" % try_file
                print(msg)
                sublime.status_message(msg)
