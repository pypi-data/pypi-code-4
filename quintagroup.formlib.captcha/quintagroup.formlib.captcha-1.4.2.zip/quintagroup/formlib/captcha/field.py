from zope.interface import implements
from zope.schema import ASCIILine
from interfaces import ICaptcha


class Captcha(ASCIILine):
    implements(ICaptcha)
