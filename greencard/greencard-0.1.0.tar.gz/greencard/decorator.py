from functools import wraps
from librarian.library import Library


class GreenCard(object):
    """
    A decorator for providing a unittesting function/method with every card in
    a librarian card library database when it is called.
    """
    def __init__(self, library):
        if isinstance(library, Library):
            self.library = library
        else:
            self.library = Library(library)

    def __call__(self, func):
        @wraps(func)
        def Wrapped(*args, **kwargs):
            """Give the wrapped function every card."""
            for card in self.library.retreive_all():
                func(*args, card=card, **kwargs)
        return Wrapped
