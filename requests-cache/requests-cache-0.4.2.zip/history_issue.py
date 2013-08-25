from contextlib import contextmanager
import requests_cache
import requests


resp = requests.get("http://httpbin.org/redirect/4")
for r in resp.history:
    print("url: {} request.url: {}".format(r.url, r.request.url))


@contextmanager
def cache_enabled(*args, **kwargs):
    requests_cache.install_cache(*args, **kwargs)
    try:
        yield
    finally:
        requests_cache.uninstall_cache()

with requests_cache.enabled('test.db'):
    resp = requests.get("http://httpbin.org/get")
    print getattr(resp, 'from_cache', False)
    s = requests.session()
    for i in range(5):
        s.get("http://httpbin.org/redirect/3")

resp = requests.get("http://httpbin.org/get")
print getattr(resp, 'from_cache', False)