import urllib

from lfs.plugins import PaymentMethodProcessor
from lfs.plugins import PM_ORDER_IMMEDIATELY


class CartasiPaymentMethodProcessor(PaymentMethodProcessor):
    """
    Implements the Cartasi payment processor.
    """

    def process(self):
        return {
            "accepted": True,
            "next_url": self.get_pay_link(),
        }

    def get_create_order_time(self):
        return PM_ORDER_IMMEDIATELY

    def get_pay_link(self):
        # cartasi requires a POST while LFS performs a GET
        # We redirect to a form that performs a POST to cartasi

        data = {
                'ORDER_ID': self.order.id,
               }

        url_string =  urllib.urlencode(data)
        return "cartasi/postform_cartasi?%s" % url_string
