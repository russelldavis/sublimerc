import sublime
import sublime_plugin

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
