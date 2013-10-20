# -*- coding: utf-8 -*-
"""
Implémentation du logger pour utiliser un buffer

Le buffer est en fait un simple dict qui stock tout les messages ajoutés dans une liste 
pour chaque type de message (info, error, etc..).

Il ajoute aussi des méthodes supplémentaire pour nettoyer le buffer si besoin.
"""
from new import LOGGER_OUTPUTS_PASSTHRU_ARGNAME, LoggerInterface
from terminal import TerminalLoggerApp
from logs import LoggingLoggerApp

class BufferLoggerApp(object):
    default_config_buffer = {
        'buffer': {
            'verbosity': 0,
            'object': {},
        },
    }
 
    def connect_buffer(self, **opts):
        """
        Méthode de connection de la sortie
        """
        pass

    def _add_message_to_buffer(self, kind, content):
        """
        Méthode d'ajout d'un message au buffer
        """
        if kind not in self._outputs['buffer']['object']:
            self._outputs['buffer']['object'][kind] = []
        self._outputs['buffer']['object'][kind].append(content)

    def flush_buffer(self, kind=None):
        """
        Méthode de nettoyage du buffer
        
        Si "kind" n'est pas spécifié le buffer sera complètement réinitialisé, sinon 
        seulement le buffer du type fourni.
        """
        if not kind:
            self._outputs['buffer']['object'] = self.default_config_buffer['buffer']['object']
        else:
            if kind in self._outputs['buffer']['object']:
                self._outputs['buffer']['object'][kind] = []

    def get_buffer_entries(self, kind=None):
        """
        Méthode de lecture d'un type d'entrées du buffer
        """
        if kind == None:
            return self._outputs['buffer']['object']
        if kind in self._outputs['buffer']['object']:
            return self._outputs['buffer']['object'][kind]
        return []

    def set_output_buffer(self, msg, kind, lv=1, indent="", **kwargs):
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
        
        :type with_buffer: bool
        :param with_buffer: (optional) Indique si la sortie est autorisée à remonter le 
                        message. Par défaut 'True'.
        """
        opts = self._outputs['buffer']
        passthru = LOGGER_OUTPUTS_PASSTHRU_ARGNAME % 'buffer'
        if opts.get('object', None) != None and kwargs.get(passthru, True) and opts['verbosity'] > 0 and opts['verbosity'] >= lv:
            self._add_message_to_buffer(kind, self._get_formatted_output('buffer', kind, indent+msg))

class BufferLoggerInterface(LoggerInterface, LoggingLoggerApp, BufferLoggerApp):
    pass
    
if __name__ == "__main__":
    obj = BufferLoggerInterface()
    obj.configure_output('buffer', verbosity=1)
    obj.title('Title this !')
    obj.debug('Debug this !')
    obj.info('Info this !')
    obj.warning('Warning this !')
    obj.error('Error this 1 !')
    obj.error('Error this 2 !')
    
    print obj.get_buffer_entries('error')
    
    obj.error('Error this 3 !')
    
    print obj.get_buffer_entries('error')
    
    obj.flush_buffer('error')
    obj.error('Error this 42 !')
    
    print obj.get_buffer_entries('error')
