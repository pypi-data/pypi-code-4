from scrapy import signals
from scrapy import log
from scrapy.exceptions import NotConfigured
from scrapy.conf import settings
from pyes import ES

class Sender(object):

    def __init__(self, crawler):
        uri = "%s:%d" % (settings['ELASTICSEARCH_SERVER'], settings['ELASTICSEARCH_PORT'])
        self.es = ES([uri], bulk_size=settings['ELASTICSEARCH_BULK_SIZE'])

    @classmethod
    def from_crawler(cls, crawler):
        # instantiate the extension object
        ext = cls(crawler)
        # connect the extension object to signals
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        # return the extension object
        return ext

    def item_scraped(self, item, spider):
        self.store(item, spider)

    def store(self, item, spider):
        self.es.index(dict(item),
                settings['ELASTICSEARCH_INDEX'],
                settings['ELASTICSEARCH_TYPE'],
                bulk=True)

