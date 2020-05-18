class Event:
    def __init__(self):
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)
        # So this can be used as a decorator.
        return listener

    def remove_listener(self, listener):
        self.listeners.remove(listener)

    def emit(self, *args, **kwargs):
        for f in self.listeners:
            f(*args, **kwargs)
