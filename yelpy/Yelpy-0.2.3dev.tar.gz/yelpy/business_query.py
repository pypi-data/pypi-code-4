import urllib


class BusinessQuery(dict):

    SERVER_URL = "http://api.yelp.com/v2/business/"

    def __init__(self, business_id):
        super(BusinessQuery, self).__init__()
        self.business_id=business_id

    def to_url(self):
        return "{0}{1}".format(self.SERVER_URL, urllib.quote(self.business_id))
