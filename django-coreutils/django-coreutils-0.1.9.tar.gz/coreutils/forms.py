# coding: utf8


class RequestFormMixin(object):
    """
    Makes a form require a request object in the contructor, setting it to
    a local instance attribute.
    """

    def __init__(self, request, *args, **kwargs):
        self.request = request
        return super(RequestFormMixin, self).__init__(*args, **kwargs)
