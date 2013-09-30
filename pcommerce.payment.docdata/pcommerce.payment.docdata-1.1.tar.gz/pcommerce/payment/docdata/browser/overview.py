from zope.interface import implements

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from pcommerce.core.interfaces import IPaymentView, IOrder


class DocdataOverview(BrowserView):
    template = ViewPageTemplateFile('overview.pt')
    implements(IPaymentView)

    def __init__(self, payment, request):
        self.payment = payment
        self.context = payment.context
        self.request = request

    def __call__(self):
        return self.template()

    def action(self):
        return self.payment.action(IOrder(self.context))
