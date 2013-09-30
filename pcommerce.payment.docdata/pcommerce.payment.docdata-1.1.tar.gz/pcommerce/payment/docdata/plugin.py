import math

from zope.interface import implements, Interface
from zope.component import adapts
from zope.component import getUtility
from zope.i18n.interfaces import IUserPreferredLanguages
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry

from pcommerce.core.interfaces import IPaymentMethod
from pcommerce.core.currency import CurrencyAware
from pcommerce.core import PCommerceMessageFactory as _
from pcommerce.payment.docdata.interfaces import IDocdataPayment, \
        IDocdataSettings
from docdata.interface import PaymentInterface
import logging

logger = logging.getLogger('pcommerce.payment.docdata')

class DocdataPayment(object):
    implements(IPaymentMethod, IDocdataPayment)
    adapts(Interface)

    title = _(u'Docdata')
    description = _('Payment using Docdata')
    icon = u'++resource++pcommerce_payment_docdata_icon.png'
    logo = u'++resource++pcommerce_payment_docdata_logo.png'

    def __init__(self, context):
        self.context = context
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IDocdataSettings)
        self.payment_interface = PaymentInterface(debug=self.docdata_debug)

    def __getattr__(self, name):
        if hasattr(self.settings, name):
            return getattr(self.settings, name)
        raise AttributeError

    def mailInfo(self, order, lang=None, customer=False):
        return _('docdata_mailinfo', default=u"Payment processed over Docdata")

    def verifyPayment(self, order):
        """
        check whether the returned values from Docdata are valid
        to prevent fraude

        check with docdata what the result of the payment was..
        we use the reporting 'txt_simple', which provides enough info

        In the docdata interface module these states are converted
        to a map containing 2 booleans (paid + closed)
        """
        params = self.context.REQUEST.form

        # sanity check..
        if int(params['form_id']) != order.orderid:
            return False

        cluster = getattr(order.paymentdata, '_cluster')

        status_params = {}
        status_params['merchant_name'] = self.docdata_merchant_name
        status_params['merchant_password'] = self.docdata_merchant_password
        status_params['payment_cluster_key'] = cluster['payment_cluster_key']
        status_params['report_type'] = 'txt_simple2'
        result = self.payment_interface.status_payment_cluster(**status_params)

        # if no exception was raised, we know we have valid results here
        status = None

        if result['paid']:
            if result['closed']:
                status = 'paid_closed'
            else:
                status = 'paid_open'
        else:
            if result['closed']:
                status = 'unpaid_cancelled'
            else:
                status = 'unpaid_pending'

        assert status
        order.paymentdata._payment_status = status
        logger.info("docdata payment result: %s" % status)

        return result['paid']

    def getLanguage(self):
        """
        """
        languages = IUserPreferredLanguages(self.context.REQUEST)
        langs = languages.getPreferredLanguages()
        if langs:
            language = langs[0]
        else:
            plone_props = getToolByName(self.context, 'portal_properties')
            language = plone_props.site_properties.default_language
        language = language.split('-')
        return language[0]

    def _create_cluster_request(self, order):
        """
        return parameters which is to be used for creating
        a new payment cluster
        """
        logger.info("_create_cluster_request")
        language = self.getLanguage()
        price = CurrencyAware(order.totalincl)
        amount = math.ceil(price.getRoundedValue(0.01))
        currency = order.currency.upper() or self.currency or 'EUR'
        days_pay_period = 0

        email = self.email or order.address.email
        firstname = self.firstname or order.address.firstname
        lastname = self.lastname or order.address.lastname
        address = self.address
        if not address:
            address = order.address.address1
            if order.address.address2:
                address += " - %s" % order.address.address2
        zip = self.zip or order.address.zip
        city = self.city or order.address.city
        country = self.country or order.address.country

        request = {}
        request['merchant_name'] = self.docdata_merchant_name
        request['merchant_password'] = self.docdata_merchant_password
        request['merchant_transaction_id'] = order.orderid
        request['profile'] = self.docdata_profile
        request['client_id'] = 'pcommerce docdata'
        request['price'] = amount
        request['cur_price'] = currency
        request['client_email'] = email
        request['client_firstname'] = firstname
        request['client_lastname'] = lastname
        request['client_address'] = address
        request['client_zip'] = zip
        request['client_city'] = city
        request['client_country'] = country
        request['client_language'] = language
        request['days_pay_period'] = days_pay_period
        return request

    def _create_url_request(self, cluster_key):
        """
        return parameters which is to be used for creating a new URL request
        """
        logger.info("_create_url_request")
        suffix_url = "/processDocdata?form_id="
        update_url = self.context.absolute_url() + suffix_url
        request = {}
        request['merchant_name'] = self.docdata_merchant_name
        request['payment_cluster_key'] = cluster_key
        request['return_url_success'] = update_url
        request['return_url_canceled'] = update_url
        request['return_url_pending'] = update_url
        request['return_url_error'] = update_url
        return request

    def action(self, order):
        """"""
        cluster_params = self._create_cluster_request(order)
        cluster = self.payment_interface.new_payment_cluster(
                **cluster_params)
        setattr(order.paymentdata, '_cluster', cluster)
        url_params = self._create_url_request(cluster['payment_cluster_key'])
        url = self.payment_interface.show_payment_cluster_url(**url_params)
        return url

