import sublime
import sublime_plugin

# This is necessary because of an annoying property of the word break (\b)
# matcher in regular expressions (which sublime uses for the 'find_under'
# command[1]): a newline on its own does *not* match \b. So, if you're
# searching for \bfoo!\b, it will not find lines that end with `foo!`. Which
# makes the find_under command useless for method names that don't end in word
# characters (i.e., anything ending in a `?` or `!`).
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
# [1] The 'whole word' option in the find panel suffers from the same problem.
class SmartFindUnder(sublime_plugin.WindowCommand):
    def run(self):
        settings = self.window.active_view().settings()
        old_setting = settings.get("word_separators")
        try:
            settings.set("word_separators", "./\\()\"'-:,.;<>~@#$%^&*|+=[]{}`~?!")
            self.window.run_command("find_under")
        finally:
            settings.set("word_separators", old_setting)
