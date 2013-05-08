import importlib
from django.conf import settings
from auction.utils.loader import load_class

AUCTION_BIDBASKET_MODEL = getattr(settings, 'AUCTION_BIDBASKET_MODEL',
    'auction.models.defaults.BidBasket')

BidBasket = load_class(AUCTION_BIDBASKET_MODEL, 'AUCTION_BIDBASKET_MODEL')