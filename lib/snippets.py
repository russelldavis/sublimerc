# Old workaround for a bug that is now fixed.
# See https://forum.sublimetext.com/t/dev-build-3156/33722/4
# class FixedCommandPaletteInputSelectionCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         self.window.run_command( "show_overlay", {"overlay": "command_palette"} )
#         self.window.run_command( "select_all" )


# class ReplFlavourInputHandler(sublime_plugin.TextInputHandler):
#     def placeholder(self):
#         return "Select a REPL flavour"

#     def list_items(self):
#         return ["JVM", "Browser", "Node"]


# class OpenClojureRepl(sublime_plugin.TextCommand):
#     def run(self, edit, repl_flavour):
#         pass

#     def input(self, args):
#         return ReplFlavourInputHandler()


