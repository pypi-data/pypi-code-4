
from urllib import quote

from zope.component import adapts
from Products.Archetypes import PloneMessageFactory as _

from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.content.link import ATLink

from raptus.multilanguagefields import widgets
import fields

from base import DefaultExtender

class LinkExtender(DefaultExtender):
    adapts(ATLink)

    fields = DefaultExtender.fields + [
        fields.StringField('remoteUrl',
            required=True,
            searchable=True,
            primary=True,
            default = "http://",
            # either mailto, absolute url or relative url
            validators = (),
            widget = widgets.StringWidget(
                description = '',
                label = _(u'label_url', default=u'URL')
            )
        ),
    ]

# patch getRemoteUrl of ATLink to support language aware catalog metadata

def __new_getRemoteUrl(self, **kwargs):
    """Sanitize output
    """
    value = self.Schema()['remoteUrl'].get(self, **kwargs)
    if not value: value = '' # ensure we have a string
    if isinstance(value, dict):
        for k, v in value.items():
            value[k] = quote(v, safe='?$#@/:=+;$,&%')
        return value
    return quote(value, safe='?$#@/:=+;$,&%')

ATLink.getRemoteUrl = __new_getRemoteUrl
