# -*- coding: utf-8 -*-
"""
Objet de base d'un jobs

Ne fait strictement rien si ce n'est montrer le nécessaire requis à implémenter.
"""
class BaseJob(object):
    # Label du job pour sa désignation
    label = "Base Job Label"
    
    # Aide optionnelle sur le job
    help = "There is no help for this job type"
    
    # Temps de programmation d'éxécution par CRON
    # - Si None, le job sera considéré comme faisant partie des jobs communs à exécuter 
    #   selon la programmation commune;
    # - Si rempli, doit être une programmation valide pour crontab, le job sera exécuté 
    #   selon cette programmation spécifique;
    cron_time = None
    # Indication sur la programmation
    cron_help = None
    
    ## Exemple de programmation spécifique, toute les 5minutes
    #cron_time = "*/5 * * * *"
    #cron_help = "Toute les 5minutes"
    
    def __init__(self, logger, debug=False):
        """
        :type logger: object `Sveetchies.logger.LoggingInterface`
        :param logger: Objet du logger que peut utiliser le job pour ses sorties d'infos
        
        :type debug: bool
        :param debug: Option pour activer le mode de débuggage qui doit permettre d'
                      activer tout le processus d'un job sans les parties 
                      émettrices/créatrices/éditrices de données. Cependant 
                      l'implémentation de cette option reste à la charge du code du job.
        """
        self.logger = logger
        self.debug = debug
    
    def do(self, **context):
        """
        Ceci est la méthode qui doit contenir le code à éxécuter pour la tâche
        
        C'est cette méthode que ``django-admin.py queues --job=XXX`` va appeler pour 
        éxécuter la tâche.
        
        :type context: dict
        :param context: Dictionnaire d'éléments de contexte spécifique (non 
                        utilisé actuellement)
        """
        pass
