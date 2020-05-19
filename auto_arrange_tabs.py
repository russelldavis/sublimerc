from .lib import settled_event


@settled_event.add_listener
def on_settled_async(view):
    window = view.window()
    group, index = window.get_view_index(view)
    if index != 0:
        # print("moving from %d" % index)
        window.set_view_index(view, group, 0)
