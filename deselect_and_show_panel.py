import sublime
import sublime_plugin

# Intended for use with the 'find' panel. Clears the selection before showing
# the panel so that it will always be prepopulated with the last thing searched
# for (across all tabs), regardless of any selection.
class DeselectAndShowPanel(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        self.window.run_command("deselect")
        self.window.run_command("show_panel", kwargs)
