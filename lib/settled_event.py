from .event import Event


# This has to be separated from settled_event_listener to avoid double imports,
# due to the way sublime automatically imports modules at the top level.
# settled_event_listener will access private members.
_event = Event()
add_listener = _event.add_listener
remove_listener = _event.remove_listener
