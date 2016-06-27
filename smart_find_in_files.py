import sublime
import sublime_plugin
import time

# Clears the Find Results tab when opening the find_in_files panel, so results
# from multiple finds don't get intermingled.
class SmartFindInFiles(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        find_results_view = self.get_find_results_view()
        if find_results_view:
            # Some plugins like BetterFindBuffer set it to read-only
            find_results_view.set_read_only(False)
            find_results_view.run_command("select_all")
            find_results_view.run_command("right_delete")
        self.window.run_command("show_panel", dict(kwargs, panel="find_in_files"))


    def get_find_results_view(self):
        for view in self.window.views():
            if view.file_name() is None and view.name() == "Find Results":
                return view
