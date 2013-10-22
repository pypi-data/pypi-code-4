# -*- coding: utf-8 -*-
"""
Module de gestion de queue de tâches

Le code ``autodiscover`` provient du code source de Django dans ``django.contrib.admin``.

Requis :

* Django >= 1.1.x

============
Installation
============

Ce module est à installer comme application d'un projet Django dans 
``settings.INSTALLED_APPS`` tel que : ::

    INSTALLED_APPS = (
        'Sveetchies.django.queues',
        ...
        'yourapps'
    )

Puis de la même manière que pour le "autodiscover" de l'administration 
(``django.contrib.admin``), insérer le code suivant au début du fichier ``urls.py`` à la 
base de votre projet Django : ::

    from Sveetchies.django import queues
    queues.autodiscover()

===========
Utilisation
===========

Registre des tâches de vos applications
---------------------------------------

Les tâches (jobs) sont enregistrés en ajoutant un fichier ``queue.py`` dans le répertoire 
de vos applications. Dans ce fichier, vous devrez créer une class implémentant 
`Sveetchies.django.queues.job.BaseJob` puis ajouter cet objet au registre des tâches de 
la façon suivante : ::

    queues.site.register(NomDeMonObjetDeJob)

Une fois fait, la tâche "NomDeMonObjetDeJob" deviendra disponible.

Outil CLI
---------

Une fois installé, une commande "queues" sera disponible dans django-admin.py, utilisez 
la commande help pour avoir un détail de l'outil : ::

    django-admin.py help queues
    
Cette outil permet de lancer les tâches enregistrées dans vos applications de votre 
projet Django : ::

    django-admin.py queues --job=NOM_DE_LA_TACHE

Pour voir la liste des tâches disponibles :

    django-admin.py queues --browse
    
Pour afficher le contenu à ajouter au crontab : ::

    django-admin.py queues --install

"""
from Sveetchies.django.queues.sites import QueueSite, site
from Sveetchies.django.queues.job import BaseJob

from django.utils.importlib import import_module

__version__ = '0.1.5'

# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
LOADING = False

def autodiscover():
    """
    Auto-discover INSTALLED_APPS admin.py modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """
    # Bail out if autodiscover didn't finish loading from a previous call so
    # that we avoid running autodiscover again when the URLconf is loaded by
    # the exception handler to resolve the handler500 view.  This prevents an
    # admin.py module with errors from re-registering models and raising a
    # spurious AlreadyRegistered exception (see #8245).
    global LOADING
    if LOADING:
        return
    LOADING = True

    import imp
    from django.conf import settings
    #import settings

    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an admin.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for admin.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own admin registration.
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's admin.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its admin.py doesn't exist
        try:
            imp.find_module('queue', app_path)
        except ImportError:
            continue

        # Step 3: import the app's admin file. If this has errors we want them
        # to bubble up.
        import_module("%s.queue" % app)
    # autodiscover was successful, reset loading flag.
    LOADING = False
