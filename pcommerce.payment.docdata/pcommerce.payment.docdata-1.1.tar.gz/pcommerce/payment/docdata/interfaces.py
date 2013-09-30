from zope.interface import Interface
from zope import schema
from pcommerce.payment.docdata import MessageFactory as _


class IDocdataPayment(Interface):
    """ Docdata payment plugin
    """


class IDocdataSettings(Interface):


    docdata_merchant_name = schema.TextLine(title=_(u"DocData merchant name"),
            description=_(u"login name for Docdata"),
            required=True,
            default=u'')

    # should be schema.Password field, but the password field sucks..
    docdata_merchant_password = schema.TextLine(title=_(
        u"DocData merchant password"),
            description=_(u"Password for docdata"),
            required=True,
            default=u'')

    docdata_profile = schema.TextLine(title=_(
        u"DocData profile"),
            description=_(u"Use 'standard' unless configurered otherwise "\
                    "in docdata"),
            required=True,
            default=u'standard')

    docdata_debug = schema.Bool(title=_(u"DocData debug mode"),
            description=_(u"Use Docdata's test environment. "\
                    "NOTE: NEVER ENABLE IN PRODUCTION"),
            required=False,
            default=False)

    currency = schema.TextLine(title=_(u"Currency"),
            description=_(u"Currency as known in Docdata (e.g. USD, EUR)"),
            required=True,
            default=u'EUR')

    email = schema.TextLine(title=_(u"client email"),
            description=_(u"You can override the email that is being used to crete the payment with Docdata. If you leave it empty, the value that has been entered by the customer will be used"),
            required=False,
            default=u'')

    firstname = schema.TextLine(title=_(u"client firstname"),
            description=_(u"You can override the firstname that is being used to crete the payment with Docdata. If you leave it empty, the value that has been entered by the customer will be used"),
            required=False,
            default=u'')

    lastname = schema.TextLine(title=_(u"client lastname"),
            description=_(u"You can override the lastname that is being used to crete the payment with Docdata. If you leave it empty, the value that has been entered by the customer will be used"),
            required=False,
            default=u'')

    address = schema.TextLine(title=_(u"client address"),
            description=_(u"You can override the email that is being used to crete the payment with Docdata. If you leave it empty, the value that has been entered by the customer will be used"),
            required=False,
            default=u'')

    zip = schema.TextLine(title=_(u"Zip"),
            description=_(u"You can override the zipcode that is being used to crete the payment with Docdata. If you leave it empty, the value that has been entered by the customer will be used"),
            required=False,
            default=u'')

    city = schema.TextLine(title=_(u"City"),
            description=_(u"You can override the city that is being used to crete the payment with Docdata. If you leave it empty, the value that has been entered by the customer will be used"),
            required=False,
            default=u'')

    country = schema.TextLine(title=_(u"Country"),
            description=_(u"You can override the country that is being used to crete the payment with Docdata. If you leave it empty, the value that has been entered by the customer will be used. Please note that Docdata is rather pickey about the submitted value. it expects a value like 'NL'"),
            required=False,
            default=u'NL')


