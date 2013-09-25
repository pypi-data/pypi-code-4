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

    consumer_key = schema.TextLine(
        title=_('twitterportlet_consumer_key',
                default=u'Twitter API Consumer key'),
        description=_('twitterportlet_consumer_key_help',
                      default=(u'Enter your Consumer Key from the Twitter API. '
                               u'See https://dev.twitter.com/apps')),
    )

    consumer_secret = schema.TextLine(
        title=_('twitterportlet_consumer_secret',
                default=u'Twitter API Consumer secret'),
        description=_('twitterportlet_consumer_secret_help',
                      default=u'Enter your Consumer Secret from the Twitter API.'),
    )

    access_token_key = schema.TextLine(
        title=_('twitterportlet_access_token_key',
                default=u'Twitter API Access token key'),
        description=_('twitterportlet_access_token_key_help',
                      default=u'Enter your Access token key from the Twitter API.'),
    )

    access_token_secret = schema.TextLine(
        title=_('twitterportlet_access_token_secret',
                default=u'Twitter API Access token secret'),
        description=_('twitterportlet_access_token_secret_help',
                      default=u'Enter your Access token secret from the Twitter API.'),
    )
