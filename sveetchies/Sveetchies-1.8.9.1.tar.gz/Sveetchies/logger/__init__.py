# -*- coding: utf-8 -*-
"""
Module d'interface des logging et sorties de debug

WARNING: Une nouvelle réimplémentation plus "modulaire" est disponible dans "new", elle 
         ouvre son support à d'autres types de sorties que le simple "print" et 
         "logging".

Ce module dispose une interface unique de messages d'application qui gèrent leur 
redirection vers un fichier de log et la sortie d'affichage, chacun des deux étant 
optionnel. Une mise en forme de la sortie d'affichage (couleur du texte) est faite en 
fonction du type de message passé (selon la méthode employée 
"error, info, title, etc..").

Pour chaque message, on peut spécifier son indentation, son niveau de verbosité requis 
pour être affichée (séparément pour les logs et la sortie d'affichage) et même si le 
message ne doit pas être redirigé vers les logs ou la sortie d'affichage.

Selon la verbosité définit à l'instanciation (ou à la connection), certains types de 
messages peuvent ne pas être redirigés vers les sorties, par exemple par défaut avec une 
verbosité de niveau 0 seul les messages d'erreurs sont redirigés, il faut un niveau 1 
pour afficher aussi les infos et warning, un niveau 2 pour les debug.

===========
Utilisation
===========

D'abord on instancie le logger : ::

    logger = LoggingInterface(passive=True, logging_filename="monfichier.log", logger_id='my-logger', error_blocker=False)

Le Logger est instancié en mode passif, il ne connectera pas l'objet logging 
automatiquement, il faudra le faire implicitement, il est aussi en mode 
non-bloquant (error_blocker) sur les erreurs, c'est à dire qu'il ne fera que remonter 
l'erreur mais ne provoquera pas automatiquement l'arrêt du script. Au contraire si cette 
argument est True, dès qu'une erreure sera spécifiée il stoppera automatiquement le 
script en cours.

Ensuite on connecte l'objet de logging et de sortie d'affichage, si besoin on peut 
redéfinir des arguments de configuration déja spécifiés dans l'instanciation, ici 
on change la verbosité : ::

    logger.connect_logger(
        output_verbosity=0,
        logging_verbosity=1,
    )

(Il est possible de se passer de cette étape en configurant la majorité des options lors 
de l'instanciation de `LoggingInterface`)

On peut ensuite directement envoyé des messages à l'interface, par exemple un titre : ::

    logger.title(u"Hello World")

Un simple message d'information : ::

    logger.info(u"Ping")

Une erreure : ::

    logger.error(u"Ouch !")

Ou une erreure bloquante (en surpassant l'option de l'instanciation) : ::

    logger.error(u"Critical error, stopping all operations !", error_blocker=True)

"""
import sys, logging
from Sveetchies.cli import termcolors

LOGGING_FILENAME = "sveetchies_logger.log"
LOGGING_DATE_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOGGING_FILEMODE = "a"

class DummyInterface(object):
    """
    Interface bidon qui ne fait strictement rien
    """
    def __init__(self, **kwargs):
        pass
    
    def info( self, msg, lv=0, log=True, output=True ):
        pass
    
    def error( self, msg, lv=0, log=True, output=True ):
        pass

class LoggingInterface(object):
    """
    Interface de logging et sortie de terminal
    """
    def __init__(self, logging_verbosity=0, output_verbosity=0, logging_filename=LOGGING_FILENAME, logging_date_format=LOGGING_DATE_FORMAT, logging_filemode=LOGGING_FILEMODE, passive=False, logger_id='sveetchies-logger', error_blocker=False):
        """
        :type logging_verbosity: int
        :param logging_verbosity: (optional) Niveau de verbosité pour l'enregistrement de logs
        
        :type output_verbosity: int
        :param output_verbosity: (optional) Niveau de verbosité pour la sortie d'affichage
        
        :type logging_filename: string
        :param logging_filename: (optional) Nom du fichier de logs à remplir (si 
                                 l'option de logging est activé). Par défaut 
                                 "sveetchies_logger.log".
        
        :type logging_date_format: string
        :param logging_date_format: (optional) Format de la ligne d'une entrée dans les 
                                    logs, voyez la documentation de `logging` pour plus 
                                    de détails. Par défaut le format est 
                                    ``DATE [LEVEL] MESSAGE``.
        
        :type logging_filemode: string
        :param logging_filemode: (optional) Mode d'ouverture du pointeur de fichier pour 
                                 le fichier de logs, correspond au mode d'un File object.
                                 Par défaut "a", donc le fichier est ouvert en écriture 
                                 en mode "append" (ajout à la fin du fichier).
        
        :type passive: bool
        :param passive: True indique que l'objet de logging soit immédiatement 
                        enregistré au moment de l'init de cette interface, False 
                        n'enregistre pas l'objet de logging, il faudra le faire 
                        manuellement via ``self.connect_logger``. False par défaut.
        
        :type logger_id: string
        :param logger_id: (optional) Identifiant du logger utilisé avec ``logging`` pour 
                          "cloisonner" les logs à un espace définit. L'identifiant par 
                          défaut est "sveetchies-logger".
        
        :type error_blocker: bool
        :param error_blocker: (optional) True indique qu'une erreur stop totalement le 
                              script en cours. False par défaut, qui indique de ne rien 
                              faire.
        """
        self.output_verbosity = output_verbosity
        self.logging_verbosity = logging_verbosity
        self.logging_filename = logging_filename
        self.logging_date_format = logging_date_format
        self.logging_filemode = logging_filemode
        self.passive = passive
        self.logger_id = logger_id
        self.error_blocker = error_blocker
        self.connect_logger( passive=passive, output_verbosity=output_verbosity, logging_verbosity=logging_verbosity, logging_filename=logging_filename, logging_date_format=logging_date_format, logging_filemode=logging_filemode, logger_id=logger_id )
        
    def connect_logger( self, **kwargs):
        """
        Redéfinit des paramètres du logger et connecte l'objet de logging (en mode non-
        passif seulement).
        
        N'importe quel argument accepté par ``__init__`` est accepté dans les kwargs pour 
        modifier un paramètre initial, sauf l'argument ``error_blocker``.
        """
        # Redéfinition de paramètres
        if 'output_verbosity' in kwargs:
            self.output_verbosity = kwargs['output_verbosity']
        if 'logging_verbosity' in kwargs:
            self.logging_verbosity = kwargs['logging_verbosity']
        if 'logging_filename' in kwargs:
            self.logging_filename = kwargs['logging_filename']
        if 'logging_date_format' in kwargs:
            self.logging_date_format = kwargs['logging_date_format']
        if 'logging_filemode' in kwargs:
            self.logging_filemode = kwargs['logging_filemode']
        if 'passive' in kwargs:
            self.passive = kwargs['passive']
        if 'logger_id' in kwargs:
            self.logger_id = kwargs['logger_id']
        # Connection
        if self.logging_verbosity > 0 and not self.passive:
            logging.basicConfig(level=logging.DEBUG, format=self.logging_date_format, filename=self.logging_filename, filemode=self.logging_filemode)
            self.logger = logging.getLogger(self.logger_id)
    
    def title( self, msg, lv=1, log=True, output=True, indent="" ):
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
        formatter = termcolors.make_style(opts=('underscore',))
        self.set(msg, formatter, kind='info', lv=lv, log=log, output=output, indent=indent)
    
    def info( self, msg, lv=1, log=True, output=True, indent="" ):
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
        formatter = termcolors.make_style()
        self.set(msg, formatter, kind='info', lv=lv, log=log, output=output, indent=indent)
    
    def debug( self, msg, lv=2, log=True, output=True, indent="" ):
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
        formatter = termcolors.make_style(opts=('italic',))
        self.set(msg, formatter, kind='debug', lv=lv, log=log, output=output, indent=indent)
    
    def warning( self, msg, lv=1, log=True, output=True, indent="" ):
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
        formatter = termcolors.make_style(fg='yellow')
        self.set(msg, formatter, kind='info', lv=lv, log=log, output=output, indent=indent)
    
    def error( self, msg, lv=0, log=True, output=True, indent="", error_blocker=False ):
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
        formatter = termcolors.make_style(fg='red', opts=('bold',))
        self.set(msg, formatter, kind='error', lv=lv, log=log, output=output, indent=indent)
        # Stoppe toute exécution de script
        if self.error_blocker or error_blocker:
            sys.exit(0)

    def set( self, msg, formatter, kind='info', lv=1, log=True, output=True, indent="" ):
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
        if log and self.logging_verbosity > 0 and self.logging_verbosity >= lv:
            getattr(self.logger, kind)(indent+msg)
        if output and self.output_verbosity > 0 and self.output_verbosity >= lv:
            print formatter(indent+msg)
    
