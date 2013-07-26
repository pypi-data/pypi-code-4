# -*- coding: utf-8 -*-
"""
Implémentation du logger pour la sortie sur la sortie standard de terminal

Utilise la mise en forme ANSI pour mettre en forme les messages de certains types, par 
exemple les titres sont soulignés, les erreurs en rouge et gras, les warning en 
orange, etc..
"""
from new import LOGGER_OUTPUTS_PASSTHRU_ARGNAME, LoggerInterface
from Sveetchies.cli import termcolors

class TerminalLoggerApp(object):
    default_config_terminal = {
        'terminal': {
            'verbosity':0,
            'formatter': termcolors.colorize,
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
                'success': {
                    'fg': 'green',
                    'opts': ('bold',),
                },
            },
        },
    }
 
    def connect_terminal(self, **opts):
        """
        Méthode de connection de la sortie
        
        (rien à faire pour "print")
        """
        pass

    def set_output_terminal(self, msg, kind, lv=1, indent="", **kwargs):
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
        
        :type with_terminal: bool
        :param with_terminal: (optional) Indique si la sortie est autorisée à remonter le 
                        message. Par défaut 'True'.
        """
        opts = self._outputs['terminal']
        passthru = LOGGER_OUTPUTS_PASSTHRU_ARGNAME % 'terminal'
        if kwargs.get(passthru, True) and opts['verbosity'] > 0 and opts['verbosity'] >= lv:
            print self._get_formatted_output('terminal', kind, indent+msg)

class TerminalLoggerInterface(LoggerInterface, TerminalLoggerApp):
    """
    Interface complète implémentant la sortie terminal
    """
    pass
    
if __name__ == "__main__":
    obj = TerminalLoggerInterface()
    obj.configure_output('terminal', verbosity=1)
    obj.title('Title this !')
    obj.debug('Debug this !')
    obj.info('Info this !')
    obj.info('Hidded', lv=2)
    obj.warning('Warning this !')
    obj.warning('Not for terminal !', with_terminal=False)
    obj.error('Error this !')
