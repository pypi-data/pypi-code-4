# -*- coding: utf-8 -*-
"""
Implémentation du logger pour la sortie dans un fichier de logging (via le module Python 
"logging")
"""
import logging

from new import LOGGER_OUTPUTS_PASSTHRU_ARGNAME, LoggerInterface
from terminal import TerminalLoggerApp

LOGGING_FILENAME = "sveetchies_logger.log"
LOGGING_DATE_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOGGING_FILEMODE = "a"

class LoggingLoggerApp(object):
    default_config_logging = {
        'logging': {
            'verbosity': 0,
            'filename': LOGGING_FILENAME,
            'date_format': LOGGING_DATE_FORMAT,
            'filemode': LOGGING_FILEMODE,
            'object': None,
        }
    }
        
    def connect_logging(self, **opts):
        """
        Méthode de connection de la sortie
        """
        if opts['verbosity'] > 0 and not self.passive:
            if 'date_format' not in opts or 'filename' not in opts or 'filemode' not in opts:
                # TODO: Implémenter une exception et un vrai message pour expliquer 
                # qu'il manque des options. En théorie ce n'est pas censé arriver si 
                # on ne supprime pas explicitement ces éléments du dico des options
                raise("FOO")
            logging.basicConfig(level=logging.DEBUG, format=opts['date_format'], filename=opts['filename'], filemode=opts['filemode'])
            logging.getLogger(self.logger_id)
            self._outputs['logging']['object'] = logging
    
    def set_output_logging(self, msg, kind, lv=1, indent="", **kwargs):
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
        
        :type with_logging: bool
        :param with_logging: (optional) Indique si la sortie est autorisée à remonter le 
                        message. Par défaut 'True'.
        """
        opts = self._outputs['logging']
        passthru = LOGGER_OUTPUTS_PASSTHRU_ARGNAME % 'logging'
        attrname = kind
        if kind == 'title':
            attrname = 'info'
        if opts.get('object', None)!=None and kwargs.get(passthru, True) and opts['verbosity'] > 0 and opts['verbosity'] >= lv:
            getattr(opts['object'], attrname)(self._get_formatted_output('logging', kind, indent+msg))

class LoggingLoggerInterface(LoggerInterface, TerminalLoggerApp, LoggingLoggerApp):
    """
    Interface complète implémentant la sortie terminal et logging
    """
    pass
    
if __name__ == "__main__":
    obj = LoggingLoggerInterface()
    obj.configure_output('terminal', verbosity=3)
    obj.configure_output('logging', verbosity=3)
    obj.connect(passive=False)
    obj.title('Title this !')
    obj.debug('Debug this !')
    obj.info('Info this !')
    obj.warning('Warning this !')
    obj.warning('Verbosity level 4 required', lv=4)
    obj.warning('Not for terminal !', with_terminal=False)
    obj.warning('Not for logging !', with_logging=False)
    obj.error('Error this !')
