from yelpy_signer import YelpySigner
from search_query import SearchQuery
from business_query import BusinessQuery
import urllib2
import json

class YelpyClient(object):

    total_calls = 0

    def __init__(self, consumer_key=None, consumer_secret=None, token=None, token_secret=None, max_calls=None):
        super(YelpyClient, self).__init__()
        self.signer = YelpySigner(consumer_key, consumer_secret, token, token_secret)
        self.max_calls = max_calls

    def validate_limit(self):
        if self.max_calls is not None and self.total_calls > self.max_calls:
            raise Exception
        self.total_calls += 1

    def validate_result(self, result):
        error = result.get('error', None)
        if error is not None:
            error_type = error.get('id', None)
            if error_type == 'EXCEEDED_REQS':
                raise Exception
            else:
                #Unknown Exception
                raise Exception
        return result
    
    def search(self, term=None, limit=None, offset=None, sort=None, category_filter=None, radius_filter=None, deals_filter=None, cc=None, lang=None, lang_filter=None, **kwargs):
        self.validate_limit()
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
        result = self.connect(signed_url)
        return self.validate_result(result)

    def business(self, business_id):
        self.validate_limit()
        bq = BusinessQuery(
            business_id=business_id
        )
        signed_url = self.signer.sign(bq.to_url())
        result = self.connect(signed_url)
        return self.validate_result(result)


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
