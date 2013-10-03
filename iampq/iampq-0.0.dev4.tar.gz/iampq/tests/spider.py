import HTMLParser
import time
import urlparse
from datetime import timedelta
from tornado import httpclient, gen, ioloop

import toro

@gen.coroutine
def spider(base_url, concurrency):
    q = toro.JoinableQueue()
    sem = toro.BoundedSemaphore(concurrency)

    start = time.time()
    fetching, fetched = set(), set()

    @gen.coroutine
    def fetch_url():
        current_url = yield q.get()

        try:
            if current_url in fetching:
                return

            print 'fetching', current_url
            fetching.add(current_url)
            urls = yield get_links_from_url(current_url)
            fetched.add(current_url)

            for new_url in urls:
                if new_url.startswith(base_url):
                    yield q.put(new_url)
        finally:
            q.task_done()
            sem.release()

    @gen.coroutine
    def worker():
        while True:
            yield sem.acquire()
            fetch_url()

    q.put(base_url)
    worker()
    yield q.join(deadline=timedelta(seconds=300))
    assert fetching == fetched
    print 'Done in %d seconds, fetched %s URLS.' % (
        time.time() - start, len(fetched))

@gen.coroutine
def get_links_from_url(url):
    try:
        response = yield httpclient.AsyncHTTPClient().fetch(url)
        print 'fetched', url
        urls = [urlparse.urljoin(url, remove_fragment(new_url))
                for new_url in get_links(response.body)]
    except Exception, e:
        print e, url
        raise gen.Return([])
    raise gen.Return(urls)

def remove_fragment(url):
    scheme, netloc, url, params, query, fragment = urlparse.urlparse(url)
    return urlparse.urlunparse((scheme, netloc, url, params, query, ''))


def get_links(html):
    class URLSeeker(HTMLParser.HTMLParser):
        def __init__(self):
            HTMLParser.HTMLParser.__init__(self)
            self.urls = []

        def handle_starttag(self, tag, attrs):
            href = dict(attrs).get('href')
            if href and tag == 'a':
                self.urls.append(href)

    url_seeker = URLSeeker()
    url_seeker.feed(html)
    return url_seeker.urls


if __name__ == '__main__':
    import logging
    logging.basicConfig()
    loop = ioloop.IOLoop.current()
    
    def stop(future):
        loop.stop()
        future.result()  # Raise error if there is one
        
    future = spider('http://google.com', 100)
    future.add_done_callback(stop)
    loop.start()