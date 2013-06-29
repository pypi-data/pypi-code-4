class CrawlerHttpException(Exception):

    def __init__(self, http_code, error):
        self.http_code = http_code
        self.error = error

    def __str__(self):
        return "[%s] %s" % (self.http_code, self.error)
