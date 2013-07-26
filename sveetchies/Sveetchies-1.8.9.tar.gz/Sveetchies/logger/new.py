# -*- coding: utf-8 -*-
"""
(Nouveau) Module d'interface des logging et sorties de debug

TODO: * Lever une erreur si on spécifie une verbosité qui n'est pas un numérique, 
        pour éviter la confusion avec du code qui passe un nombre dans un string;
      * Propager la nouvelle réimplémentation sur ceux qui en dépendent, lorsque les 
        applis critiques seront mises à jour, le contenu du module "new" prendra la 
        place de celui du __init__, ce dernier restant temporairement sous le nom de 
        "old" pour compatibilité descendante.

=======
CHANGES
=======

* L'interface de base n'implémente plus aucune sortie par défaut, il faut passer par 
    ses héritiers;
* Le système d'héritage détache l'api de la sortie sur une "OutputApp" qui est à 
    ajouter à l'héritage, de cette facon on peut cumuler plusieurs API de sorties 
    différentes dans un même héritage;
* Les sorties implémentent leur propre système de formatage si besoin;
* Les options de chaque sortie sont définis par défaut dans la "OutputApp" à 
    l'initialisation, ensuite il faut utiliser la méthode "connect_Output" pour 
    modifier les options par défaut;

=====
USAGE
=====

Instanciation du logger de base qui n'implémente aucune sortie
--------------------------------------------------------------

    from Sveetchies.logger.new import LoggerInterface

    # Init du logger
    logger = LoggerInterface(
        passive=True,
        logger_id='mysuper-logger',
        error_blocker=False
    )
    # démo
    logger.info("Foo")
    logger.error("Foo")

* passive : En mode passif le logger ne se connecte pas à ses sorties, la connection est 
  ce qui permet d'activer les paramètres de fonctionnement fournis. Dans le 
  cas de certains types de sorties (par exemple un backend SQL), il est utile 
  de ne pas se connecter directement. En général on ne connecte le logger aux 
  sorties que lorsque tout leur paramètres ont été passés.
* logger_id : identifiant unique du logger, pour éviter les clashs avec d'autres logger 
  en parallèle, ceci est aussi et surtout utile à un logger de Logging.
* error_blocker : si activé, toute erreure (via un "logger.error(..)") déclenchera la 
  fin du programme en cours via un sys.exit(0). C'est un peu une façon d'émuler le concept 
  d'une Exception via le logger.

Instanciation d'un logger pour la sortie de terminal et fichier de logs
-----------------------------------------------------------------------

    from Sveetchies.logger.logs import LoggingLoggerInterface

    # Init du logger
    logger = LoggingLoggerInterface(
        passive=True,
        logger_id='mysuper-logger',
        error_blocker=False
    )
    # Configuration des sorties
    logger.configure_output('terminal', verbosity=1)
    logger.configure_output('logging', filename="monfichier.log", verbosity=1)
    
    # démo
    logger.info("Foo")
    logger.error("Foo")

Si vous n'avez pas besoin de "logging" utilisez simplement TerminalLoggerApp qui ne fait 
qu'utiliser la sortie de terminal.
"""
import sys

LOGGER_OUTPUTS_CONNECT_FUNCNAME = "connect_%s"
LOGGER_OUTPUTS_SET_FUNCNAME = "set_output_%s"
LOGGER_OUTPUTS_PASSTHRU_ARGNAME = "with_%s"
LOGGER_OUTPUTS_CONFIG_ARGNAME = "default_config_%s"
LOGGER_DEFAULT_ID = 'sveetchies-logger'

class DummyInterface(object):
    """
    Interface bidon qui ne fait strictement rien
    """
    def __init__(self, **kwargs):
        pass
    def title( self, *args, **kwargs):
        pass
    def info( self, *args, **kwargs):
        pass
    def success( self, *args, **kwargs):
        pass
    def debug( self, *args, **kwargs):
        pass
    def warning( self, *args, **kwargs):
        pass
    def error( self, *args, **kwargs):
        pass

class LoggerInterface(object):
    """
    Interface du logger
    
    Ceci est l'implémentation de base, en l'état elle n'utilise aucune sortie, voyez 
    plutôt ses descendants comme "terminal" ou "loggin"
    """
    def __init__(self, **kwargs):
        """
        :type passive: bool
        :param passive: True indique que l'objet de logging soit immédiatement 
                        enregistré au moment de l'init de cette interface, False 
                        n'enregistre pas l'objet de logging, il faudra le faire 
                        manuellement via ``self.connect``. False par défaut.
        
        :type logger_id: string
        :param logger_id: (optional) Identifiant du logger utilisé avec ``logging`` pour 
                          "cloisonner" les logs à un espace définit. L'identifiant par 
                          défaut est "sveetchies-logger".
        
        :type error_blocker: bool
        :param error_blocker: (optional) True indique qu'une erreur stop totalement le 
                              script en cours. False par défaut, qui indique de ne rien 
                              faire.
        """
        self.passive = kwargs.get('passive', False)
        self.logger_id = kwargs.get('logger_id', LOGGER_DEFAULT_ID)
        self.error_blocker = kwargs.get('error_blocker', False)
        self._outputs = {
            #OUTPUT_KEY_NAME: {
            #    'verbosity': OUTPUT_VERBOSITY_LEVEL,
            #    'formatter': OPTIONS_DICT,
            #    'object': OUTPUT_MANAGER_OBJECT_IF_ANY,
            #    ANY_OUTPUT_SPECIFIC_OPTIONS
            #},
        }
        # Recherche toute les "OutputApp" existantes pour les inscrire au registre des 
        # options de sorties
        for item in dir(self):
            if item.startswith(LOGGER_OUTPUTS_CONFIG_ARGNAME%""):
                self._outputs.update(getattr(self, item))
        # Connection automatique (si non mode non passif) à l'initialisation
        self.connect( passive=self.passive, logger_id=self.logger_id, error_blocker=self.error_blocker )
        
    def configure_output( self, name, **kwargs):
        """
        Configure les options d'un type de sortie
        
        Tout les arguments "kwargs" sont ajoutés au registre des options de la sortie.
        
        :type name: string
        :param name: Nom clé du type de sortie à configurer
        """
        self._outputs[name].update(kwargs)
        
    def connect( self, **kwargs):
        """
        Redéfinit des paramètres du logger et connecte les types de sorties
        
        N'importe quel argument accepté par ``__init__`` est accepté dans les kwargs pour 
        modifier un paramètre initial.
        """
        # Redéfinition de paramètres
        if 'passive' in kwargs:
            self.passive = kwargs['passive']
        if 'logger_id' in kwargs:
            self.logger_id = kwargs['logger_id']
        if 'error_blocker' in kwargs:
            self.error_blocker = kwargs['error_blocker']
        
        # Connections des différentes sorties configurés
        if not self.passive:
            for k,v in self._outputs.items():
                if hasattr(self, LOGGER_OUTPUTS_CONNECT_FUNCNAME%k) and v.get('verbosity', 0)>0:
                    getattr(self, LOGGER_OUTPUTS_CONNECT_FUNCNAME%k)(**v)
        
    def _get_formatted_output(self, output_name, kind, content):
        """
        Retourne le message formaté selon les options de formattage du type de sortie 
        spécifiée, si elle en a
        """
        opts = self._outputs[output_name]
        if 'formatter' in opts and opts['formatter'] and 'formats' in opts:
            if kind in opts['formats']:
                return opts['formatter'](content, **opts['formats'][kind])
        return content

    def set(self, msg, kind='info', lv=1, indent="", **kwargs):
        """
        Redirection du message vers les sorties disponibles et selon ses options
        
        :type msg: string
        :param msg: Message.
        
        :type formatter: function
        :param formatter: Formatter du texte utilisé pour la sortie de terminal
        
        :type kind: string
        :param kind: (optional) Type de message ('info', 'debug', 'error','warning', 
                     etc.. Ce doit être un nom d'attribut de log valide pour le module 
                     'logging'), 'info' par défaut.
        
        :type lv: int
        :param lv: Niveau de verbosité requis LoggerInterface pour afficher ce message.
        
        :type log: bool
        :param log: (optional) Indique si le message doit etre loggué, True par défaut.
        
        :type output: bool
        :param output: (optional) Indique si le message doit etre affiché dans la sortie 
                       de terminal, True par défaut.
        
        :type indent: string
        :param indent: (optional) Chaîne d'indentation, vide par défaut
        """
        # Force la conversion en string de tout ce qui n'est pas une chaîne de caractère
        if not isinstance(msg, basestring):
            msg = str(msg)
        # Remonte le message à toute les sorties enregistrés et actifs (avec une 
        # verbosité supérieur à 0)
        for k,v in self._outputs.items():
            if hasattr(self, LOGGER_OUTPUTS_SET_FUNCNAME%k) and v.get('verbosity', 0)>0:
                getattr(self, LOGGER_OUTPUTS_SET_FUNCNAME%k)(msg, kind=kind, lv=lv, indent=indent, **kwargs)

    def title(self, msg, lv=1, log=True, output=True, indent="", **kwargs):
        """
        Message de titre
        
        :type msg: string
        :param msg: Message.
        
        :type lv: int
        :param lv: Niveau de verbosité requis LoggerInterface pour afficher ce message.
        
        :type log: bool
        :param log: (optional) Indique si le message doit etre loggué, True par défaut.
        
        :type output: bool
        :param output: (optional) Indique si le message doit etre affiché dans la sortie 
                       de terminal, True par défaut.
        
        :type indent: string
        :param indent: (optional) Chaîne d'indentation, vide par défaut
        """
        self.set(msg, kind='title', lv=lv, log=log, output=output, indent=indent, **kwargs)
    
    def info(self, msg, lv=1, log=True, output=True, indent="", **kwargs):
        """
        Message d'information
        
        :type msg: string
        :param msg: Message.
        
        :type lv: int
        :param lv: Niveau de verbosité requis LoggerInterface pour afficher ce message.
        
        :type log: bool
        :param log: (optional) Indique si le message doit etre loggué, True par défaut.
        
        :type output: bool
        :param output: (optional) Indique si le message doit etre affiché dans la sortie 
                       de terminal, True par défaut.
        
        :type indent: string
        :param indent: (optional) Chaîne d'indentation, vide par défaut
        """
        self.set(msg, kind='info', lv=lv, log=log, output=output, indent=indent, **kwargs)
    
    def success(self, msg, lv=1, log=True, output=True, indent="", **kwargs):
        """
        Message de succès d'un évènement
        
        Identique de nature à un info(), permet juste une mise en forme différente
        
        :type msg: string
        :param msg: Message.
        
        :type lv: int
        :param lv: Niveau de verbosité requis LoggerInterface pour afficher ce message.
        
        :type log: bool
        :param log: (optional) Indique si le message doit etre loggué, True par défaut.
        
        :type output: bool
        :param output: (optional) Indique si le message doit etre affiché dans la sortie 
                       de terminal, True par défaut.
        
        :type indent: string
        :param indent: (optional) Chaîne d'indentation, vide par défaut
        """
        self.set(msg, kind='success', lv=lv, log=log, output=output, indent=indent, **kwargs)
    
    def debug(self, msg, lv=2, log=True, output=True, indent="", **kwargs):
        """
        Message de debug
        
        :type msg: string
        :param msg: Message.
        
        :type lv: int
        :param lv: Niveau de verbosité requis LoggerInterface pour afficher ce message.
        
        :type log: bool
        :param log: (optional) Indique si le message doit etre loggué, True par défaut.
        
        :type output: bool
        :param output: (optional) Indique si le message doit etre affiché dans la sortie 
                       de terminal, True par défaut.
        
        :type indent: string
        :param indent: (optional) Chaîne d'indentation, vide par défaut
        
        :rtype: None
        :return: None
        """
        self.set(msg, kind='debug', lv=lv, log=log, output=output, indent=indent, **kwargs)
    
    def warning(self, msg, lv=1, log=True, output=True, indent="", **kwargs):
        """
        Message d'alerte
        
        :type msg: string
        :param msg: Message.
        
        :type lv: int
        :param lv: Niveau de verbosité requis LoggerInterface pour afficher ce message.
        
        :type log: bool
        :param log: (optional) Indique si le message doit etre loggué, True par défaut.
        
        :type output: bool
        :param output: (optional) Indique si le message doit etre affiché dans la sortie 
                       de terminal, True par défaut.
        
        :type indent: string
        :param indent: (optional) Chaîne d'indentation, vide par défaut
        """
        self.set(msg, kind='warning', lv=lv, log=log, output=output, indent=indent, **kwargs)
    
    def error(self, msg, lv=0, log=True, output=True, indent="", error_blocker=False, **kwargs):
        """
        Message d'erreur
        
        :type msg: string
        :param msg: Message.
        
        :type lv: int
        :param lv: Niveau de verbosité requis LoggerInterface pour afficher ce message.
        
        :type log: bool
        :param log: (optional) Indique si le message doit etre loggué, True par défaut.
        
        :type output: bool
        :param output: (optional) Indique si le message doit etre affiché dans la sortie 
                       de terminal, True par défaut.
        
        :type indent: string
        :param indent: (optional) Chaîne d'indentation, vide par défaut
        
        :type error_blocker: bool
        :param error_blocker: (optional) True indique qu'une erreur stop totalement le 
                              script en cours. False par défaut, qui indique de ne rien 
                              faire.
        """
        self.set(msg, kind='error', lv=lv, log=log, output=output, indent=indent, **kwargs)
        # Stoppe toute exécution de script
        if self.error_blocker or error_blocker:
            sys.exit(0)
    
if __name__ == "__main__":
    obj = LoggerInterface()
    obj.title('Title this !')
    obj.debug('Debug this !')
    obj.info('Info this !')
    obj.warning('Warning this !')
    obj.error('Error this !')
