# -*- coding: utf-8 -*-
"""
Interface dans syncdb pour synchroniser les templates enregistrés en bdd
"""
from django.db.models import signals 
from django.conf import settings

from Sveetchies.django import mailings

PROMPT_MESSAGE = """
[Mailings app] Do you want to synchronize regitered templates and their missing templates in database ? (yes/no)
"""

def test_setup(**kwargs):
    """
    Vérifie que tout les contrôleurs de templates inscrit au registre ont bien leur 
    template en bdd et si non, ils sont injectés en bdd.
    
    Le système est non destructif, les templates existant déjà en bdd ne sont jamais 
    écrasés.
    """
    mailings.autodiscover()
    
    interactive = kwargs.get('interactive', False)
    verbosity = kwargs.get('verbosity', 0)

    # Recherche des templates enregistrés n'existant pas en bdd
    missing_keys = []
    for k,v in mailings.site.get_registry().items():
        try:
            mailings.models.Template.objects.get(key=k)
        except mailings.models.Template.DoesNotExist:
            missing_keys.append(k)
    
    # Ajoute tout les templates marqués manquants
    if len(missing_keys)>0:
        # En mode interactif, on demande la permission d'insérer les données initiales.
        # Répondre oui injecte les données, répondre non ne fait rien (utile si on veut 
        # remplir avec des fixtures).
        # En mode non interactif, le comportement par défaut est d'injecter les données 
        # sans demander.
        populate = True
        if interactive:
            # ask for permission to create the test
            populate = raw_input(PROMPT_MESSAGE).strip()
            while not (populate == "yes" or populate == "no"):
                populate = raw_input("\nPlease type 'yes' or 'no': ").strip()
            if populate == "no":
                return
        
        i = 0
        for key in missing_keys:
            obj = mailings.site._registry[key](passive=True, auto_escaping=True)
            mailings.models.Template(**obj.get_initial_datas()).save()
            i += 1
        if verbosity>0:
            print "Installed %s registered template from mailings app" % i

signals.post_syncdb.connect(test_setup, sender=mailings.models) 
