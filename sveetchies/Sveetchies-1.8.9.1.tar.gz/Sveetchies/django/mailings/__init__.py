# -*- coding: utf-8 -*-
"""
Sveetchies-mailings est un système de gestion d'envois de mails

Le système utilise des templates modifiables dans l'administration et un historique 
optionnel des envois.

Le principe est de créer des objets pour chaque template de mail souhaité, ces objets 
sont des contrôleurs qui font interface entre le template, son modèle de données et 
le système d'envoi de mail inclus dans Django.

Le système de template utilisé est celui de Django sans restriction, le contexte du 
template n'est pas celui d'un ``RequestContext`` mais d'un simple ``Context`` rempli 
avec le contexte indiqué à l'instance.

L'historique lorsqu'il est activé, enregistre tout les emails qui ont été envoyés, une 
entrée pour chaque destinataire, avec tout son contenu généré (rendus des templates 
avec leur contexte). Une option supplémentaire ``historize_content`` est disponible pour 
chaque contrôleur et permet lorsqu'elle vaut ``False`` de ne pas enregistrer le contenu 
généré (par exemple pour raisons de sécurités ou confidentialités). Cette option peut aussi 
être contrôlée globalement via la variable ``MAILINGS_HISTORIZE_CONTENT`` des settings de 
la webapp, l'attribut ``historize_content`` d'un contrôleur (hormis ``BaseMailTemplate``) 
prends toujours la main sur cette option global.

Le code ``autodiscover`` provient du code source de Django dans ``django.contrib.admin``.

TODO: * Essayer de créer un genre de super controleur capable de faire un réel 
        send_mass_mail qui enverrait tout les mails en une seule fois. Le principe de 
        WizardForm doit être intéressant comme base.
      * Sinon aussi, il y l'idée d'un super controleur toujours, mais juste en charge 
        d'une queue de controleur et avec une interconnexion qui lui permettrait de tout 
        envoyer avec un send_mass_mail en une seule fois dès le bon signal reçu
"""
from Sveetchies.django.mailings.sites import MailingSite, site
from Sveetchies.django.mailings.interface import BaseMailTemplate

from django.utils.importlib import import_module

__version__ = '0.1.6'

# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
LOADING = False

def autodiscover():
    """
    Auto-discover INSTALLED_APPS mails.py modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """
    # Bail out if autodiscover didn't finish loading from a previous call so
    # that we avoid running autodiscover again when the URLconf is loaded by
    # the exception handler to resolve the handler500 view.  This prevents an
    # mails.py module with errors from re-registering models and raising a
    # spurious AlreadyRegistered exception (see #8245).
    global LOADING
    if LOADING:
        return
    LOADING = True

    import imp
    from django.conf import settings
    
    # Load modules directly
    for mod in getattr(settings, 'MAILINGS_LOADS', ()):
        try:
            import_module(mod)
        except ImportError:
            continue

    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an mails.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for mails.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own admin registration.
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's mails.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its mails.py doesn't exist
        try:
            imp.find_module('mails', app_path)
        except ImportError:
            continue

        # Step 3: import the app's mails file. If this has errors we want them
        # to bubble up.
        import_module("%s.mails" % app)
    # autodiscover was successful, reset loading flag.
    LOADING = False
