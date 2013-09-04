"""
Allow redirections from start_urls, even if redirections are not enabled
"""

__version__ = '0.1.0'

from scrapy.contrib.downloadermiddleware.redirect import RedirectMiddleware


class HomepageRedirectMiddleware(RedirectMiddleware):

    def __init__(self, settings, crawler, redirect):
        self.max_metarefresh_delay = settings.getint('REDIRECT_MAX_METAREFRESH_DELAY')
        self.max_redirect_times = settings.getint('REDIRECT_MAX_TIMES')
        self.priority_adjust = settings.getint('REDIRECT_PRIORITY_ADJUST')
        self.crawler = crawler
        self.redirect = redirect

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        redirect = settings.getbool('REDIRECT_ENABLED')
        return cls(settings, crawler, redirect)

    def process_spider_output(self, response, result, spider):
        if self.redirect:
            return result

        # Only authorize redirections for start_url
        redirect = [301, 302, 303, 307]
        if response.url in spider.start_urls and response.status in redirect:
            # use the RedirectMiddleware.process_response method to perform
            # the redirection
            return [self.process_response(response.request, response, spider)]
        return result
