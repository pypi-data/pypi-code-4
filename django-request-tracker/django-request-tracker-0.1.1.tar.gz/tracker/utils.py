from tracker.settings import tracker_settings


def send_pageview(request, response):
    tracker_backends = tracker_settings.DEFAULT_BACKENDS

    for backend in tracker_backends:
        tracker = backend()
        tracker.page(request, response)
