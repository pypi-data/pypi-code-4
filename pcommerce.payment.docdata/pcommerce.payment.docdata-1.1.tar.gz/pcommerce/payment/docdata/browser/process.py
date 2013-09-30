from zope.interface import implements
from Products.Five.browser import BrowserView
from pcommerce.core.interfaces import IPaymentProcessor
from pcommerce.core.interfaces import IPaymentView
from pcommerce.core.interfaces import IOrderRegistry
from pcommerce.payment.docdata import MessageFactory as _


class ProcessDocdata(BrowserView):
    """process Docdata payments
    """

    implements(IPaymentView)

    def __init__(self, context, request):
        super(ProcessDocdata, self).__init__(context, request)
        self.context = context
        self.request = request
        self.form = self.context.REQUEST.form
        self.processor = IPaymentProcessor(self.context)

    def status_description(self):
        """ return the docdata status """
        orderId = self.form.get('form_id', '')
        orderId = int(orderId)
        registry = IOrderRegistry(self.context)
        order = registry.getOrder(orderId)
        status = order.paymentdata._payment_status
        status_description = _(status)
        return status_description

    def processOrder(self):
        """ do the actual processing in the plugin """
        orderId = self.form.get('form_id', '')
        return self.processor.processOrder(orderId,
                'pcommerce.payment.docdata')
