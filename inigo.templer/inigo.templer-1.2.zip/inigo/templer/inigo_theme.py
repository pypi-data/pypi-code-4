import copy

from inigo.templer.inigo_plone import InigoPlone
from templer.core.vars import StringVar, EASY, EXPERT

from templer.localcommands import SUPPORTS_LOCAL_COMMANDS
from templer.localcommands import LOCAL_COMMANDS_MESSAGE


class InigoTheme(InigoPlone):
    _template_dir = 'templates/inigo_theme'
    summary = 'A comprehensive Plone package for Inigo theme projects'
