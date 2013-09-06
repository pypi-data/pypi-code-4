from celery.task.http import HttpDispatch, HttpDispatchTask, URL
from tornado import httpclient
from tornado import gen

httpclient.AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')

class NonBlockingHttpDispatch(HttpDispatch):
    r"""NonBlockingHttpDispatch is responsible for sending
    nonblocking http requests and collect the task result."""

    @gen.coroutine
    def make_request(self, url, method, params):
        http_client = httpclient.AsyncHTTPClient()
        response = yield (http_client.fetch(url, params))
        if response.error:
            return self._handle_error(response)
        else:
            return response.body

    def dispatch(self):
        """Dispatch callback and return result."""
        return super(NonBlockingHttpDispatch, self).dispatch()

    def handle_error(self, response):
        response.rethrow()

class NonBlockingHttpDispatchTask(HttpDispatchTask):

    def run(self, url=None, method='GET', **kwargs):
        url = url or self.url
        method = method or self.method
        return NonBlockingHttpDispatch(url, method, kwargs).dispatch()

class CeleryHttp(URL):
    """HTTP Callback URL

    Supports requesting an URL asynchronously.

    :param url: URL to request.
    :keyword dispatcher: Class used to dispatch the request.
        By default this is :class:`HttpDispatchTask`.
    """
    dispatcher = NonBlockingHttpDispatchTask

    @gen.coroutine
    def get_async(self, callback=None, **kwargs):
        async_res = yield gen.Task(self.dispatcher.apply_async,
            args=(str(self), 'GET'), kwargs=kwargs)
        raise gen.Return(async_res)

    @gen.coroutine
    def post_async(self, **kwargs):
        async_res = yield gen.Task(self.dispatcher.apply_async,
            args=(str(self), 'POST'), kwargs=kwargs)
        raise gen.Return(async_res)