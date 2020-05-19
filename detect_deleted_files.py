import sublime
import sublime_plugin
import os
import time

"""Detects open tabs whose files have been deleted.

If any of the implicated tabs have a dirty buffer, shows an alert.
Implicated tabs without dirty buffers are closed.
"""
class DetectDeletedFiles(sublime_plugin.EventListener):
    def __init__(self):
        self.last_deactivation = None

    def update_existence(self, view):
        view.settings().set("ddf_exists", self.view_file_exists(view))

    def on_load_async(self, view):
        self.update_existence(view)

    def on_post_save_async(self, view):
        self.update_existence(view)

    def on_deactivated_async(self, view):
        self.last_deactivation = time.time()

    def on_activated_async(self, view):
        if self.last_deactivation:
            elapsed = time.time() - self.last_deactivation
            # We only care about when the entire app activates.
            # Elapsed time since deactivation is a decent heuristic for that,
            # because in-app activations are immediately preceded by in-app
            # deactivations.
            if elapsed > 0.5:
                self.handle_deleted_files()

    @classmethod
    def friendly_path(cls, path):
        home_dir = os.path.expanduser('~')
        return path.replace(home_dir, '~')

    @classmethod
    def view_file_exists(cls, view):
        file_name = view.file_name()
        return bool(file_name and os.path.exists(file_name))

    @classmethod
    def handle_deleted_files(cls):
        active_window = sublime.active_window()
        dirty_deleted_file_names = []
        for window in sublime.windows():
            for view in window.views():
                existed = view.settings().get("ddf_exists")
                if existed and not cls.view_file_exists(view):
                    if view.is_dirty():
                        dirty_deleted_file_names.append(cls.friendly_path(view.file_name()))
                    else:
                        view.set_scratch(True)
                        view.close()

        if dirty_deleted_file_names:
            sublime.error_message(
                "There are dirty views whose files have been deleted: \n" +
                "\n".join(dirty_deleted_file_names))


def plugin_loaded():
    DetectDeletedFiles.handle_deleted_files()
