"""Same idea as ZenTabs, but simplified logic since we know tabs are already
ordered by MRU.

Unlike ZenTabs, this also makes it much easier to customize tabs that you
don't want to be closeable.

It also tweaks the formula: tabs that are not closable are *not* included
in the liit.
"""

from .lib import settled_event

LIMIT = 12

# Not using on_load because that can get called while a view is still
# transient -- we need to run when it becomes persistent.
@settled_event.add_listener
def on_settled_async(settled_view):
    window = settled_view.window()
    group = window.active_group()
    views = window.views_in_group(group)

    if len(views) < LIMIT:
        return

    if same_view_count(window, group, views):
        return

    active_view_id = window.active_view().id()
    num_closeable = 0
    for view in views:
        if is_closable(view):
            num_closeable += 1
            # In practice we should never end up with the active view, since
            # it should always be the first tab.
            if num_closeable > LIMIT and view.id() != active_view_id:
                view.close()


def same_view_count(window, group, views):
    last_counts = window.settings().get("limit_tabs__last_counts", {})
    # Sublime requires keys to be strings
    if last_counts.get(str(group)) == len(views):
        return
    last_counts[str(group)] = len(views)
    # settings().get() returns a copy, so we have to update with set()
    window.settings().set("limit_tabs__last_counts", last_counts)



def is_closable(view):
    return not (
        view.is_dirty()
        # Scratch buffers never get set as dirty and don't prompt to save
        # when you close them. I'm not sure how they get created other than
        # via the API.
        or view.is_scratch()
        or view.is_loading()
        or (
            view.settings().get("syntax")
            == "Packages/Default/Find Results.hidden-tmLanguage"
        )
    )
