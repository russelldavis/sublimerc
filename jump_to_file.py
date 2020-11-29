import sublime
import sublime_plugin
import webbrowser
import os
from os.path import splitext

def _try_open_file(window, try_file, path=None):
    if path:
        try_file = os.path.join(path, try_file)

    for ext in ['', '.rb', '.js']:
        with_ext = try_file + ext
        if os.path.isfile(with_ext):
            window.open_file(with_ext)
            return True

    return False


def try_open_region_file(view, region):
    window = view.window()
    # The scope includes the quote characters, so we slice them off
    try_file = view.substr(view.extract_scope(region.begin()))[1:-1]

    if os.path.isabs(try_file):
        _try_open_file(window, try_file)
        return

    folders = window.folders()
    if folders:
        for folder in folders:
            if _try_open_file(window, try_file, folder):
                return

    view_file = view.file_name()
    if view_file:
        view_dir = os.path.dirname(view_file)
        if _try_open_file(window, try_file, view_dir):
            return

    msg = "Not a file: %s" % try_file
    print(msg)
    sublime.status_message(msg)


# From https://gist.github.com/korinVR/3542836
def try_open_region_url(view, region):
    s = view.sel()[0]

    # Expand selection to possible URL
    start = s.a
    end = s.b

    view_size = view.size()
    terminator = ['\t', ' ', '\"', '\'', '(', ')']

    while (start > 0
            and not view.substr(start - 1) in terminator
            and view.classify(start) & sublime.CLASS_LINE_START == 0):
        start -= 1

    while (end < view_size
            and not view.substr(end) in terminator
            and view.classify(end) & sublime.CLASS_LINE_END == 0):
        end += 1

    # Check if this is URL
    url = view.substr(sublime.Region(start, end))
    print("URL : " + url)

    if url.startswith(('http://', 'https://')):
        webbrowser.open_new_tab(url)
    else:
        print("not URL")


class JumpToFile(sublime_plugin.TextCommand):
    def run(self, edit = None):
        view = self.view
        for region in view.sel():
            if view.score_selector(region.begin(), "parameter.url, string.quoted"):
                try_open_region_file(view, region)
            else:
                try_open_region_url(view, region)


# Derp, this is already built into sublime (the switch_file command)
#
# class JumpToHeaderOrImpl(sublime_plugin.TextCommand):
#     def run(self, edit = None):
#         view = self.view
#         window = view.window()
#         file = view.file_name()
#         if file is None:
#             return
#
#         base, file_ext = splitext(file)
#         impl_exts = [".cc", ".cpp", ".c"]
#
#         if file_ext == ".h":
#             for impl_ext in impl_exts:
#                 if _try_open(window, base + impl_ext):
#                     return
#         else:
#             for impl_ext in impl_exts:
#                 if file_ext == impl_ext:
#                     if _try_open(window, base + ".h"):
#                         return
