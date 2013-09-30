from zope.interface import implements
from Products.Five.browser import BrowserView
from pcommerce.core.interfaces import IPaymentView
from pcommerce.payment.docdata.data import DocdataPaymentData


class DocdataPayment(BrowserView):
    implements(IPaymentView)

    def __init__(self, payment, request):
        self.payment = payment
        self.context = payment.context
        self.request = request

    def validate(self):
        """
        validate the form.
        No parameters to be checked, so return True
        """
        return True

    def process(self):
        return DocdataPaymentData()

    def renders(self):
        return False
