import sublime
import sublime_plugin

""" Custom behavior when closing the last tab / last window

If a window doesn't have folders, it auto closes the window when the last tab
is closed. If the last window is being closed, it hides the application
instead.

If a window does have folders, it does not close the window when all tabs are
already closed.

If the smart_close_ignore_folders setting is True, acts like there are no
folders for the conditions above.
"""
class SmartCloseCommand(sublime_plugin.WindowCommand):
    def run(self):
        # Don't use window.settings(); those don't contain user/project overrides.
        # NB: active_view() will be a valid object even when window.views() is empty
        settings = self.window.active_view().settings()
        ignore_folders = settings.get("smart_close_ignore_folders", False)
        has_folders = self.window.folders() and not ignore_folders

        # Make cmd-w a no-op for empty windows with folders
        # (force use of cmd-shift-w to close these windows)
        if not self.window.views() and has_folders:
            return

        window_count = len(sublime.windows())
        self.window.run_command("close")

        if not has_folders and not self.window.views():
            if window_count > 1:
                # This does the equivalent of the close_windows_when_empty
                # setting, except it doesn't apply to the last window or to
                # windows that have folders.
                self.window.run_command("close")
            else:
                self.hide_sublime()
                # sublime.run_command('exit')

    @staticmethod
    def hide_sublime():
        from subprocess import Popen, PIPE
        # TODO: get the process name from applescript before running the close command,
        # or find some other way to not hardcode my custom "Sublime Edit" name here.
        # Can't just grab the frontmost process since it won't always be sublime.
        cmd = """
            tell application "Finder"
                set visible of process "Sublime Edit" to false
            end tell"""
        Popen(['/usr/bin/osascript', "-e", cmd], stdout=PIPE, stderr=PIPE)
