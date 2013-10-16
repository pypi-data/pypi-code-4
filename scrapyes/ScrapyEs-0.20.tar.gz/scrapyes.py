from scrapy import signals
from scrapy.exceptions import NotConfigured
from datetime import datetime
from pyes import ES

class Sender(object):

    def __init__(self, crawler):
        server = crawler.settings['ELASTICSEARCH_SERVER']
        port = crawler.settings['ELASTICSEARCH_PORT']
        bulk_size = crawler.settings['ELASTICSEARCH_BULK_SIZE']
        uri = "%s:%d" % (server, port)
        self.es = ES([uri], bulk_size=bulk_size)
        self.index = crawler.settings['ELASTICSEARCH_INDEX']
        self.start_time = datetime.now() 

    @classmethod
    def from_crawler(cls, crawler):
        # instantiate the extension object
        ext = cls(crawler)
        # save the start time
        # connect the extension object to signals
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        # return the extension object	
        return ext

    def item_scraped(self, item, spider):
        self.index(item, spider)

    def spider_closed(self, spider):
        self.es.force_bulk()
        query = """
        {
            "filtered": {
                "query": {
                    "term": {
                        "spider_name": %s
                    }
                },
                "filter": {
                    "range": {
                        "last_indexed": {
                            "to": %s
                        }
                    }
                }
            }
        }
        """ % (spider.__class__.name, self.start_time)
        self.es.delete_by_query(self.es_index(spider), None, query)

    def index(self, item, spider):
        es_index = self.es_index(spider)
        if 'id' in item:
            self.es.index(dict(item),
                es_index, item.__class__.__name__, id=item['id'], bulk=True)
        else:
            self.es.index(dict(item), 
                es_index, item.__class__.__name__, bulk=True)


    def es_index(self, spider):
        """obtains the elastic search index to use
        :spider: current spider
        :returns: elastic search index

        """
        if hasattr(spider, 'index') and spider.index:
            index = spider.index
        else:
            index = self.index
        return index
