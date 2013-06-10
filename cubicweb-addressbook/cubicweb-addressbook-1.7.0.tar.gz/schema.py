from yams.buildobjs import EntityType, String, Float
from yams.constraints import IntervalBoundConstraint

_ = unicode

class PhoneNumber(EntityType):
    number = String(fulltextindexed=True, required=True, maxsize=64)
    type = String(required=True, internationalizable=True,
                  vocabulary=((_('mobile'), _('home'), _('office'),
                               _('fax'), _('secretariat'))),
                  default=u'mobile')

class PostalAddress(EntityType):
    street  = String(fulltextindexed=True, required=True, maxsize=256)
    street2  = String(fulltextindexed=True, maxsize=256)
    postalcode = String(fulltextindexed=True, required=True, maxsize=256)
    city    = String(fulltextindexed=True, required=True, maxsize=256,
                     internationalizable=True) # see static-message.pot
    country = String(fulltextindexed=True, maxsize=256,
                     internationalizable=True) # see static-message.pot
    state   = String(fulltextindexed=True, maxsize=256)
    latitude = Float(constraints=[IntervalBoundConstraint(-90, 90)],
                     description=_('latitude in degree'))
    longitude = Float(constraints=[IntervalBoundConstraint(-180, 180)],
                     description=_('longitude in degree'))

class IMAddress(EntityType):
    im_account  = String(fulltextindexed=True, required=True, maxsize=64)
    type = String(required=True, internationalizable=True,
                  vocabulary=('jabber', 'icq', 'msn'),
                  default=u'jabber')
