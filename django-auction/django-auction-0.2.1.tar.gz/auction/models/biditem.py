import importlib
from django.conf import settings
from auction.utils.loader import load_class

AUCTION_BIDITEM_MODEL = getattr(settings, 'AUCTION_BIDITEM_MODEL',
    'auction.models.defaults.BidItem')

BidItem = load_class(AUCTION_BIDITEM_MODEL, 'AUCTION_BIDITEM_MODEL')