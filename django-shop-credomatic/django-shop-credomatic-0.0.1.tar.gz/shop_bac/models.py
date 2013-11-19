from shop_bac.forms import AVSRESPONSE_CHOICES, CVVRESPONSE_CHOICES, RESPONSE_CODE_CHOICES
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings

from shop.util.loader import load_class
ORDER_MODEL = getattr(settings, 'SHOP_ORDER_MODEL',
    'shop.models.defaults.order.Order')
Order = load_class(ORDER_MODEL, 'SHOP_ORDER_MODEL')


class OrderBacResponse(models.Model):
    order = models.ForeignKey(Order, related_name="responsebac",
            verbose_name=_('Order'))
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    response = models.IntegerField()
    responsetext = models.CharField(max_length=200)         # Textual response
    authcode = models.CharField(max_length=10)              # Transaction authorization code
    transactionid = models.CharField(max_length=50)         # Payment Gateway transaction id
    avsresponse = models.CharField(choices=AVSRESPONSE_CHOICES, max_length=1)
    hash = models.CharField(max_length=100)
    cvvresponse = models.CharField(choices=CVVRESPONSE_CHOICES, max_length=1)
    response_code = models.CharField(choices=RESPONSE_CODE_CHOICES, max_length=3)

    class Meta(object):
        app_label = 'shop'
