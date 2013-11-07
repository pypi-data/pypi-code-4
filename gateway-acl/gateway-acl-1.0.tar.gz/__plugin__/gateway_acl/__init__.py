'''
Created on Nov 14, 2012

@package: gateway acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the setup files for service access control layer gateway.
'''

# --------------------------------------------------------------------

NAME = 'gateway acl'
GROUP = 'gateway'
VERSION = '1.0'
DESCRIPTION = '''This plugin provides the service gateways.'''
INSTALL_REQUIRES = ['gateway >= 1.0', 'ally-core-http >= 1.0']
LONG_DESCRIPTION = '''The ACL (access control layer) gateway plugin integrates gateways that are designed based on published REST models and services, basically makes the conversion between access allowed on a service call and a gateway REST model.'''