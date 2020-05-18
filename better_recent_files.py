import sublime
import sublime_plugin
import os
from .lib import settled_event

# TODO: add support for recently_closed_files

def update_file_list(view, list_name):
    file_name = view.file_name()
    if not file_name:
        return

    window = view.window()

    # This can happen after opening (previewing) a file in transient mode
    # that no longer exists and then switching back to the previous view
    # (though we already handle that case above since file_name would be
    # None). It can also happen in that same scenario if the file exists
    # but there's some other error when opening it (e.g., "fatal: This
    # operation must be run in a work tree" when opening
    # .git/COMMIT_EDITMSG, perhaps an error from a plugin?)
    if not window:
        return

    settings = window.settings()
    files = settings.get(list_name, [])

    try:
        files.remove(file_name)
    except ValueError:
        pass

    # print("Adding ", list_name, file_name)

    files.insert(0, file_name)
    # Prevent the list from growing unbounded.
    # TODO: make this a setting.
    del files[50:]
    settings.set(list_name, files)


@settled_event.add_listener
def on_settled(view):
    update_file_list(view, 'recently_activated_files')


class RecentFilesEventListener(sublime_plugin.EventListener):
    def on_modified_async(self, view):
        update_file_list(view, 'recently_edited_files')


class ShowFileListCommand(sublime_plugin.WindowCommand):
    def friendly_path(self, path):
        for folder in self.window.folders():
            path = path.replace(folder + '/', '', 1)

        home_dir = os.path.expanduser('~')
        return path.replace(home_dir, '~')

    def run(self, name):
        settings = self.window.settings()
        files = settings.get(name, [])
        orig_active_view = self.window.active_view()

        # Filter out files that no longer exist. Don't permanently delete
        # them, because they might come back if, e.g., the user switches
        # branches in source control.
        files = list(filter(os.path.exists, files))

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
