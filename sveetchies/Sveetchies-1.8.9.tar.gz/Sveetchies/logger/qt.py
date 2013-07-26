# -*- coding: utf-8 -*-
"""
Implémentation du logger pour la sortie sur un widget text de PyQt
"""
from new import LOGGER_OUTPUTS_PASSTHRU_ARGNAME, LoggerInterface
from terminal import TerminalLoggerApp
from logs import LoggingLoggerApp

def html_markup_func(text, opts=(), **kwargs):
    """
    Returns your text, enclosed in HTML suitable for Qt
    
    (Actually, only a few set of below options is implemented)

    Depends on the keyword arguments 'fg' and 'bg', and the contents of
    the opts tuple/list.

    Returns the RESET code if no parameters are given.

    Valid colors:
        'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'

    Valid options:
        'bold'
        'underscore'
        'italic'
    
    :type text: string
    :param text: (optional) Text to enclose. Empty string by default (make it so 
                useless).
    
    :type opts: tuple
    :param opts: (optional) Formating options (like bold, italic, underscore, etc..).
    
    :rtype: string
    :return: The text string with enclosures for colors and formating
    """
    if not isinstance(text, basestring):
        text = str(text)
    if 'bold' in opts:
        text = "<b>%s</b>"%text
    if 'italic' in opts:
        text = "<i>%s</i>"%text
    if 'underscore' in opts:
        text = "<u>%s</u>"%text
    return text

class QtLoggerApp(object):
    default_config_qt = {
        'qt': {
            'verbosity':0,
            'formatter': html_markup_func,
            'object': None,
            'formats': {
                'title': {
                    'opts': ('underscore',),
                },
                'info': {},
                'debug': {
                    'opts': ('italic',),
                },
                'warning': {
                    'fg': 'yellow',
                },
                'error': {
                    'fg': 'red',
                    'opts': ('bold',),
                },
            },
        },
    }
 
    def connect_qt(self, **opts):
        """
        Méthode de connection de la sortie
        """
        pass

    def set_output_qt(self, msg, kind, lv=1, indent="", **kwargs):
        """
        Redirection du message vers la sortie
        
        :type msg: string
        :param msg: Message.
        
        :type kind: string
        :param kind: (optional) Type de message ('info', 'title', 'debug', 'error','warning', 
                     etc..
        
        :type lv: int
        :param lv: Niveau de verbosité requis par LoggerInterface pour afficher ce message.
        
        :type indent: string
        :param indent: (optional) Chaîne d'indentation, vide par défaut
        
        :type with_qt: bool
        :param with_qt: (optional) Indique si la sortie est autorisée à remonter le 
                        message. Par défaut 'True'.
        """
        opts = self._outputs['qt']
        passthru = LOGGER_OUTPUTS_PASSTHRU_ARGNAME % 'qt'
        if opts.get('object', None)!=None and kwargs.get(passthru, True) and opts['verbosity'] > 0 and opts['verbosity'] >= lv:
            opts['object'].setText( self._get_formatted_output('qt', kind, indent+msg) )

class QtLoggerInterface(LoggerInterface, LoggingLoggerApp, QtLoggerApp):
    pass
    
if __name__ == "__main__":
    obj = QtLoggerInterface()
    obj.configure_output('qt', verbosity=1)
    obj.title('Title this !')
    obj.debug('Debug this !')
    obj.info('Info this !')
    obj.warning('Warning this !')
    obj.error('Error this !')
