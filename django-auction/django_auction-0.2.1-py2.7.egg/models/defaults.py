from django.db import models
from django.utils.translation import ugettext_lazy as _
from auction.models.bases import BaseAuction, BaseAuctionLot, BaseBidBasket, BaseBidItem

class Auction(BaseAuction):
    class Meta:
        abstract = False
        app_label = 'auction'
        verbose_name = _('Auction')
        verbose_name_plural = _('Auctions')

class Lot(BaseAuctionLot):
    class Meta:
        abstract = False
        app_label = 'auction'
        verbose_name = _('Auction lot')
        verbose_name_plural = _('Auction lots')

class BidBasket(BaseBidBasket):
    class Meta:
        abstract = False
        app_label = 'auction'
        verbose_name = _('Bid basket')
        verbose_name_plural = _('Bid baskets')

class BidItem(BaseBidItem):
    class Meta:
        abstract = False
        app_label = 'auction'
        verbose_name = _('Bid item')
        verbose_name_plural = _('Bid items')