import sublime
import sublime_plugin
import sys
import os
import subprocess
import threading
import time
from subprocess import Popen, PIPE

# To use appscript directly:
# sys.path.append('/Users/russell/.pyenv/versions/3/lib/python3.3/site-packages/aeosa')
# import appscript

class CloseWithAutoExit(sublime_plugin.WindowCommand):
    def run(self):
        # Don't use window.settings(), those don't contain user/project overrides.
        # NB: active_view() will be a valid object even when window.views() is empty
        settings = self.window.active_view().settings()
        ignore_folders = settings.get("my_auto_close_ignore_folders", False)
        has_folders = self.window.folders() and not ignore_folders

        # Make cmd-w a no-op for empty windows with folders
        # (force use of cmd-shift-w to close these windows)
        if not self.window.views() and has_folders:
            return

        self.window.run_command("close")

        if not self.window.views():
            window_count = len(sublime.windows())

            # This does the equivalent of the close_windows_when_empty setting,
            # except it won't apply to windows that have folders
            if not has_folders:
                self.window.run_command("close")
                # We have deal with the window count this way because sublime.windows() won't immediately
                # reflect the closed window from the command above.
                window_count -= 1

            if window_count < 1:
                sublime.run_command('exit')

# This is necessary because of an annoying property of the word break (\b)
# matcher in regular expressions (which sublime uses for the 'find_under'
# command[1]): a newline on its own does *not* match \b. So, if you're
# searching for \bfoo!\b, it will not find lines that end with `foo!`. Which
# makes the find_under command useless for method names that don't end in word
# characters (i.e., anything ending in a `?` or `!`).
#
# This plugin hacks around the problem by adding `?` and `!` to the
# word_separators setting, so that when you run find_under on a method name
# ending with one of these symbols, it will leave off the trailing symbol.
# This isn't perfect -- it can lead to some false positive matches, but it's
# good enough, and much better than the alternative.
#
# We could just permanently add these to word_separators, but that would break
# things for sublime's symbol indexing, word selection, etc.
#
# [1] The 'whole word' option in the find panel suffers from the same problem.
class SmartFindUnder(sublime_plugin.WindowCommand):
    def run(self):
        settings = self.window.active_view().settings()
        old_setting = settings.get("word_separators")
        try:
            settings.set("word_separators", "./\\()\"'-:,.;<>~@#$%^&*|+=[]{}`~?!")
            self.window.run_command("find_under")
        finally:
            settings.set("word_separators", old_setting)


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


# From http://stackoverflow.com/a/19516653/278488
class SaveAllExistingFilesCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        for w in sublime.windows():
            self._save_files_in_window(w)

    def _save_files_in_window(self, w):
        for v in w.views():
            self._save_exiting_file_in_view(v)

    def _save_exiting_file_in_view(self, v):
        if v.file_name() and v.is_dirty():
            v.run_command("save")


class AutoArrangeTabs(sublime_plugin.EventListener):
    running = False
    logging = False

    @classmethod
    def log(cls, msg):
        if cls.logging:
            print(msg)

    def on_activated_async(self, view):
        if AutoArrangeTabs.running:
            AutoArrangeTabs.log("early return")
            return
        AutoArrangeTabs.running = True
        AutoArrangeTabsThread().start()


# This all needs to happen in a thread because if we block directly in
# on_activated_async, sublime will queue up all calls that happen while
# we're blocking, which we don't want to happen (we want those to immediately
# go away via the early return path).
class AutoArrangeTabsThread(threading.Thread):
    def run(self):
        try:
            AutoArrangeTabs.log("waiting")
            subprocess.call(['/Users/russell/src/keywait/keywait'])
            AutoArrangeTabs.log("checking")

            window = sublime.active_window()
            view = window.active_view()
            group, index = window.get_view_index(view)
            if index != 0:
                AutoArrangeTabs.log("moving from %d" % index)
                window.set_view_index(view, group, 0)

        finally:
            AutoArrangeTabs.running = False


def hide_sublime():
    cmd = """
        tell application "Finder"
            set frontProcess to first process whose frontmost is true
            set visible of frontProcess to false
        end tell"""
    Popen(['/usr/bin/osascript', "-e", cmd], stdout=PIPE, stderr=PIPE)

