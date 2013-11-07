'''
Created on Jul 15, 2011

@package: internationalization
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Nistor Gabriel

Contains the internationalization setup files.
'''

# --------------------------------------------------------------------

NAME = 'internationalization'
GROUP = 'internationalization'
VERSION = '1.0'
DESCRIPTION = 'Provides the scanning and persistance for the localized messages'
AUTHOR = 'Gabriel Nistor'
AUTHOR_EMAIL = 'gabriel.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST', 'plugin', 'internationalization']
INSTALL_REQUIRES = ['ally-api >= 1.0', 
                    'ally-plugin >= 1.0', 
                    'support-sqlalchemy >= 1.0', 
                    'support-cdm >= 1.0']