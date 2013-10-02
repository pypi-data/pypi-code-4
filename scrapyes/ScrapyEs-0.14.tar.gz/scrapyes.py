from scrapy import signals
from scrapy.exceptions import NotConfigured
from pyes import ES
import hashlib

class Sender(object):

    def __init__(self, crawler):
        server = crawler.settings['ELASTICSEARCH_SERVER']
        port = crawler.settings['ELASTICSEARCH_PORT']
        bulk_size = crawler.settings['ELASTICSEARCH_BULK_SIZE']
        uri = "%s:%d" % (server, port)
        self.es = ES([uri], bulk_size=bulk_size)
        self.index = crawler.settings['ELASTICSEARCH_INDEX']
        self.id_field = crawler.settings.get('ELASTICSEARCH_ITEM_ID_FIELD')

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
        if self.id_field is None:
            self.es.index(dict(item), index, item.__class__.__name__, bulk=True)
        else:
            hashed_id = self.hash_id(item[self.id_field])
            self.es.index(dict(item),
                    index, item.__class__.__name__, id=hashed_id, bulk=True)

    def hash_id(self, item_id):
        return hashlib.md5(item_id).hexdigest()
