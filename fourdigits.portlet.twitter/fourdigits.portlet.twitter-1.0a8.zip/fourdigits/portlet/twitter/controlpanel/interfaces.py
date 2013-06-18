from zope import schema
from zope.interface import Interface

from fourdigits.portlet.twitter import \
            FourdigitsPortletTwitterMessageFactory as _


class IFourdigitPortletTwitterSetting(Interface):
    """"""
    use_data_cache = schema.Bool(
                title=_(u'use_data_cache_title', u'Use data cache system'),
                description=_(u'use_data_cache_help', default=u''),
                default=False,)

    cache_time = schema.Int(
                title=_(u'cache_time_title', u'Cache time'),
                description=_(u'cache_time_help', default=u'Seconds in cache'),
                default=3600,
                required=True,)

    timeout = schema.Int(
                title=_(u'timeout_title', u'Timeout'),
                description=_(u'timeout_help', default=u'Timeout for calling twitter'),
                default=15,
                required=True,)

    proxyInfo = schema.Tuple(
            title=_(u'proxy_title', u"Information about Proxy"),
            description=_(u'proxy_help', u"Enter your proxy address like http://your.proxy:8080"),
            value_type=schema.TextLine(),
            required=False,)
