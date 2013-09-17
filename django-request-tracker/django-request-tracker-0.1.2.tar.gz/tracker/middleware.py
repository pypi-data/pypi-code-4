import threading

from tracker.utils import send_pageview


class TrackerSubmissionMiddleware:
    def process_response(self, request, response):
        t = threading.Thread(target=send_pageview,
                             args=[request, response])
        t.daemon = True
        t.start()

        return response
