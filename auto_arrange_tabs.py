import sublime
import sublime_plugin
import subprocess
import threading
from BetterRecentFiles import BetterRecentFiles

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
                BetterRecentFiles.RecentFilesEventListener.update_file_list(
                    view, 'recently_activated_files')

        finally:
            AutoArrangeTabs.running = False

# Make the default recently-activated listener a no-op -- AutoArrangeTabs
# updates the list in a smarter way (ignoring tabs that are passed over while
# holding down ctrl in a ctrl-tab sequence).
BetterRecentFiles.RecentFilesEventListener.on_activated_async = lambda *args: None
