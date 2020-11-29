import sublime
import sublime_plugin

# Taken from https://github.com/glutanimate/sublime-deselect
class DeselectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        end = self.view.sel()[0].b
        pt = sublime.Region(end, end)
        self.view.sel().clear()
        self.view.sel().add(pt)
