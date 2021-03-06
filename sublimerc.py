import sublime
import sublime_plugin


# Comment continuation
class SmartEnterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        stripped_line = self.view.substr(self.view.line(self.view.sel()[0])).strip()
        cursor_char = self.view.substr(self.view.sel()[0].end())
        to_insert = "\n"

        if stripped_line.startswith("#") and not stripped_line.startswith("#!"):
            # Don't add a second comment char
            # (particularly important when the cursor is at the start of the line).
            if cursor_char != "#":
                to_insert += "# "
        elif stripped_line.startswith("//"):
            if cursor_char != "/":
                to_insert += "// "

        self.view.run_command("insert", { "characters": to_insert })

# This is a replacement for the builtin paste command, which has annoying behavior after a
# copy/paste with no selection: it will put the line above whatever line you're on, *even if*
# your cursor is not at the start of the line*. Should maybe be called DumbPaste since it fixes
# logic that's trying to be too smart.
#
# They do this by adding special metadata to the item in the clipboard that only they interpret,
# which means the special behavior only works in the same app, and you'd have no way of knowing
# what was different by looking at the plain text contents of the clipboard. That was a fun one
# to track down. See https://github.com/Microsoft/vscode/issues/16341 (vs code does it too).
#
# NB: I previously tried to fix this by tweaking the copy and paste commands, but that resulted
# in Cmd+C not working in the console panel. This way is simpler as well.
#
# Additional behavior: auto-indents the contents if it begins with leading spaces (after any
# leading newlines), which is an indication that it came from an indented context, but may need
# to be reindented to fit the new context).
class SmartPaste(sublime_plugin.TextCommand):
    def run(self, edit):
        # Looks like a no-op, but it removes the metadata
        text = sublime.get_clipboard()
        sublime.set_clipboard(text)

        # Smart indent. See details above.
        lead = text.lstrip("\r\n")[0]
        if lead == " " or lead == "\t":
            self.view.run_command("paste_and_indent")
        else:
            self.view.run_command("paste")
