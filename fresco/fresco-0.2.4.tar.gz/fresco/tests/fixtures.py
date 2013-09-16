from fresco import Route, GET, Response

class CBV(object):
    """
    A class based view
    """

    __routes__ = [
        Route('/', GET, 'index_html'),
        Route('/page', GET, 'view_page'),
        Route('/page2', GET, 'view_page', tag='page2'),
    ]

    def __init__(self, s):
        self.s = s

    def index_html(self, request):
        return Response([self.s])

    def view_page(self, request):
        return Response([])


