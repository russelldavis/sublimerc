import sublime
import sublime_plugin

# This fixes two issues with the builtin find_under command:
#
# 1) There's an annoying property of the word break (\b) matcher in regular
# expressions (which sublime uses for the 'find_under' command[1]): a newline
# on its own does *not* match \b. So, if you're searching for \bfoo!\b, it
# will not find lines that end with `foo!`. Which makes the find_under command
# useless for method names that don't end in word characters (i.e., anything
# ending in a `?` or `!`).
#
# This plugin hacks around the problem by adding `?` and `!` to the
# word_separators setting, so that when you run find_under on a method name
# ending with one of these symbols, it will leave off the trailing symbol.
# This isn't perfect -- it can lead to some false positive matches, but it's
# good enough, and much better than the alternative.
#
# We could just permanently add these to word_separators, but that would break
# things for sublime's symbol indexing, word selection, etc.
#
# 2) Options for the find_under command are taken from the last find or
# find_in_files command. This makes it stateful and frustratingly
# unpredictable. It's behavior today may differ from its behavior yesterday
# due to a find_in_files you ran hours ago. There is no world in which that is
# a sane UX decision. This fixes that by reseting the find options first.
#
# [1] The 'whole word' option in the find panel suffers from the same problem.
class SmartFindUnder(sublime_plugin.WindowCommand):
    def run(self):
        self.reset_find_args()
        settings = self.window.active_view().settings()
        old_setting = settings.get("word_separators")
        try:
            settings.set("word_separators", "./\\()\"'-:,.;<>~@#$%^&*|+=[]{}`~?!")
            self.window.run_command("find_under")
        finally:
            settings.set("word_separators", old_setting)

    def reset_find_args(self):
        # Reset the find options by opening the panel (with the options) and
        # then closing it. Anyone know of a cleaner way to do this?

        args = {"panel": "find_in_files", "reverse": False, "regex": False,
                "whole_word": False, "case_sensitive": False}
        self.window.run_command("show_panel", args=dict(args, toggle=False))
        self.window.run_command("show_panel", args=dict(args, toggle=True))
