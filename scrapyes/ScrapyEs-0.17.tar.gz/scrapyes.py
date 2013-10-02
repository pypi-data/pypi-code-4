from scrapy import signals
from scrapy.exceptions import NotConfigured
from pyes import ES

class Sender(object):

    def __init__(self, crawler):
        server = crawler.settings['ELASTICSEARCH_SERVER']
        port = crawler.settings['ELASTICSEARCH_PORT']
        bulk_size = crawler.settings['ELASTICSEARCH_BULK_SIZE']
        uri = "%s:%d" % (server, port)
        self.es = ES([uri], bulk_size=bulk_size)
        self.index = crawler.settings['ELASTICSEARCH_INDEX']

    @classmethod
    def from_crawler(cls, crawler):
        # instantiate the extension object
        ext = cls(crawler)
        # connect the extension object to signals
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        # return the extension object	
        return ext

    def item_scraped(self, item, spider):
        self.store(item, spider)

    def spider_closed(self, spider):
        self.es.force_bulk()

    def store(self, item, spider):
        if hasattr(spider, 'index') and spider.index:
            index = spider.index
        else:
            index = self.index
        if 'id' in item:
            self.es.index(dict(item),
                    index, item.__class__.__name__, id=item['id'], bulk=True)
        else:
            self.es.index(dict(item), index, item.__class__.__name__, bulk=True)
