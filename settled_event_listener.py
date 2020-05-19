import sublime
import sublime_plugin
import subprocess
import threading
# See comments in settled_event for details
from .lib.settled_event import _event


LOGGING = False


def log(msg):
    if LOGGING:
        print("SettledEvent: " + msg)


class SettledEventListener(sublime_plugin.EventListener):
    thread_running = False

    def on_load_async(self, view):
        log("load")


    def on_activated_async(self, view):
        log("activated")

        if SettledEventListener.thread_running:
            log("early return")
            return

        # This can happen after previewing (opening in transient mode) a file
        # that no longer exists and then switching back to the previous view
        # (e.g., when using the better-recent-files plugin). It can also
        # happen in that same scenario if the file exists but there's some
        # other error when opening it (e.g., "fatal: This operation must be
        # run in a work tree" when opening .git/COMMIT_EDITMSG, perhaps an
        # error from a plugin?)
        if not view.window():
            log("ignoring view with no window")
            return

        # This is important because some quick-panels change the view to
        # preview the selected file, and we don't want to rearrange tabs when
        # that happens. Sublime doesn't send an on_activated event for those
        # view changes while the panel is open, but it does send one for the
        # panel itself on its initial activation (which is what we catch
        # here), which we need to ignore so that the panel's view change for
        # the initial selection doesn't get processed by our thread.
        if view != view.window().active_view():
            log("ignoring panel activation")
            return

        SettledEventListener.thread_running = True
        SettledEventThread().start()


# This all needs to happen in a thread because if we block directly in
# on_activated_async, sublime will queue up all calls that happen while
# we're blocking, which we don't want to happen (we want those to immediately
# go away via the early return path).
class SettledEventThread(threading.Thread):
    def run(self):
        try:
            log("waiting")
            subprocess.call(['/Users/russell/dev/projects/keywait/keywait'])

            view = sublime.active_window().active_view()
            # NB: file_name might be None
            log("scheduling settled_event for " + str(view.file_name()))
            # Emit on sublime's async thread to avoid potential threading issues for callers
            def emit():
                log("emitting settled_event for " + str(view.file_name()))
                _event.emit(view)
            sublime.set_timeout_async(emit, 0)
        finally:
            SettledEventListener.thread_running = False

