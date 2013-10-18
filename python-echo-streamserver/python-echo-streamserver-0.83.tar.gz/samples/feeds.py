from echo import feeds
from echo.feeds.parsers import OPMLFeedsContentHandler
from pprint import pprint

feeds_obj = OPMLFeedsContentHandler(feeds.list(parsed=False))
pprint(feeds_obj.feeds_dict)
