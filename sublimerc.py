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
            print("AutoArrangeTabs: " + msg)

    def on_activated_async(self, view):
        if AutoArrangeTabs.running:
            AutoArrangeTabs.log("early return")
            return

        # This can happen after opening (previewing) a file in transient mode
        # that no longer exists and then switching back to the previous view
        # (e.g., when using the better-recent-files plugin). It can also
        # happen in that same scenario if the file exists but there's some
        # other error when opening it (e.g., "fatal: This operation must be
        # run in a work tree" when opening .git/COMMIT_EDITMSG, perhaps an
        # error from a plugin?)
        if not view.window():
            AutoArrangeTabs.log("ignoring view with no window")
            return

        # This is important because some quick-panels change the view to
        # preview the selected file, and we don't want to rearrange tabs when
        # that happens. Sublime doesn't send an on_activated event for those
        # view changes while the panel is open, but it does send one for the
        # panel itself on its initial activation (which is what we catch
        # here), which we need to ignore so that the panel's view change for
        # the initial selection doesn't get processed by our thread.
        if view != view.window().active_view():
            AutoArrangeTabs.log("ignoring panel activation")
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


class RecentFilesEventListener(sublime_plugin.EventListener):
    def update_file_list(self, view, list_name):
        file_name = view.file_name()
        if file_name:
            settings = view.window().settings()
            files = settings.get(list_name, [])

            try:
                files.remove(file_name)
            except ValueError:
                pass

            files.insert(0, file_name)
            # Prevent the list from growing unbounded.
            # TODO: make this a setting.
            del files[50:]
            settings.set(list_name, files)

    def on_modified_async(self, view):
        self.update_file_list(view, 'recently_edited_files')

    def on_activated_async(self, view):
        self.update_file_list(view, 'recently_activated_files')


class ShowFileListCommand(sublime_plugin.WindowCommand):
    def friendly_path(self, path):
        for folder in self.window.folders():
            path = path.replace(folder + '/', '', 1)

        home_dir = os.path.expanduser('~')
        return path.replace(home_dir, '~')

    def run(self, list):
        settings = self.window.settings()
        files = settings.get(list, [])
        orig_active_view = self.window.active_view()

        # No point in showing the current file.
        try:
            # The object we get back from settings.get() is a copy, so this is
            # safe to mutate.
            files.remove(orig_active_view.file_name())
        except ValueError:
            pass

        items = [[os.path.basename(f), self.friendly_path(f)] for f in files]

        def on_done(index):
            if index >= 0:
                self.window.open_file(files[index])
            else:
                self.window.focus_view(orig_active_view)

        def on_highlight(index):
            self.window.open_file(files[index], sublime.TRANSIENT)

        flags = sublime.KEEP_OPEN_ON_FOCUS_LOST
        self.window.show_quick_panel(items, on_done, flags, 0, on_highlight)


# def hide_sublime():
#     cmd = """
#         tell application "Finder"
#             set frontProcess to first process whose frontmost is true
#             set visible of frontProcess to false
#         end tell"""
#     Popen(['/usr/bin/osascript', "-e", cmd], stdout=PIPE, stderr=PIPE)

