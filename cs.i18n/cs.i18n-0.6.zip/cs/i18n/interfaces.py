from zope.interface import Interface

class Icsi18nProductLayer(Interface):
    """ A layer specific for cs.i18n

    We will use this to register browser pages that should only be
    used when cs.i18n is installed in the site

    """
