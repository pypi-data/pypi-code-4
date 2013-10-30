from templer.core.vars import var
from inigo.templer.localcommands import SubTemplate

class UpgradeProfile(SubTemplate):
    """
    Adds an upgrade profile and handler 
    """

    _template_dir = 'templates/genericsetup/upgrade_profile'
    summary = 'Adds an upgrade profile and handler skeleton'

    vars = [
        var('upgrade_from_version', 'Profile version to upgrade from', default='*'),
        var('upgrade_to_version', 'Profile version to upgrade to'),
    ]


class SkinLayer(SubTemplate):
    """
    Adds a skin layer
    """

    _template_dir = 'templates/genericsetup/skin_layer'
    summary = 'Adds a skin layer directory'

    vars = [
        var('default_skin', 'Default skin to inherit from', default='Sunburst Theme')
    ]

class CSSResource(SubTemplate):

    _template_dir = 'templates/genericsetup/cssresource'
    summary = 'Adds a CSS resource into Plone registry'

    vars = [
        var('css_filename', 'CSS filename')
    ]

class JSResource(SubTemplate):

    _template_dir = 'templates/genericsetup/jsresource'
    summary = 'Adds a JS resource into Plone registry'

    vars = [
        var('js_filename', 'JS filename')
    ]
