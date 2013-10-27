from yelpy_signer import YelpySigner
from search_query import SearchQuery
from business_query import BusinessQuery
import urllib2
import json

class YelpyClient(object):

    def __init__(self, consumer_key=None, consumer_secret=None, token=None, token_secret=None):
        super(YelpyClient, self).__init__()
        self.signer = YelpySigner(consumer_key, consumer_secret, token, token_secret)
    
    def search(self, term=None, limit=None, offset=None, sort=None, category_filter=None, radius_filter=None, deals_filter=None, cc=None, lang=None, lang_filter=None, **kwargs):
        sq = SearchQuery(
            term=term,
            limit=limit,
            offset=offset,
            sort=sort,
            category_filter=category_filter,
            radius_filter=radius_filter,
            deals_filter=deals_filter,
            cc=cc,
            lang=lang,
            lang_filter=lang_filter,
            **kwargs
        )
        signed_url = self.signer.sign(sq.to_url())
        return self.connect(signed_url)

    def business(self, business_id):
        bq = BusinessQuery(
            business_id=business_id
        )
        signed_url = self.signer.sign(bq.to_url())
        return self.connect(signed_url)


    def connect(self, signed_url):
        try:
            conn = urllib2.urlopen(signed_url, None)
            try:
                response = json.loads(conn.read())
            finally:
                conn.close()
        except urllib2.HTTPError, error:
            response = json.loads(error.read())
        return response
