# -*- coding: utf-8 -*-
"""
Interface de base pour les objets de mails
"""
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.template import Context, Template

from django.contrib.auth.models import User

from Sveetchies.django.auth import get_user_queryset_from_perm

from models import RECEIVE_PERMISSION_KEY
from models import Template as MailTemplate
from models import History as MailHistory

# TODO: à déplacer dans le __init__ avec des ``foo = getattr(settings, NAME, DEFAULT)``
if not hasattr(settings, 'MAILINGS_SEND_DEBUG'):
    MAILINGS_SEND_DEBUG = False
else:
    MAILINGS_SEND_DEBUG = settings.MAILINGS_SEND_DEBUG

if not hasattr(settings, 'MAILINGS_WITH_HISTORY'):
    MAILINGS_WITH_HISTORY = False
else:
    MAILINGS_WITH_HISTORY = settings.MAILINGS_WITH_HISTORY

if not hasattr(settings, 'MAILINGS_HISTORIZE_CONTENT'):
    MAILINGS_HISTORIZE_CONTENT = True
else:
    MAILINGS_HISTORIZE_CONTENT = settings.MAILINGS_HISTORIZE_CONTENT

class BaseMailTemplate(object):
    """
    Contrôleur de base d'un template de mail
    
    Un contrôleur de template inscrit au registre de mailings doit implémenter les 
    méthodes de cet objet par héritage ou non. Dans le cas d'un héritage, habituellement 
    seul les attributs statiques (key, label, subject, etc..) sont nécessaires, ainsi que 
    la méthode ``get_available_variables``. Attention il ne peut y avoir qu'un seul 
    contrôleur avec le même attribut ``key`` (utilisé comme un identifiant unique) sinon 
    le registre lèvera une exception.
    
    Le contrôleur peut être appelé de manière "statique" pour récupérer ses attributs de 
    base tel que key, label, etc.. par exemple comme dans le registre.
    
    À l'utilisation "standard", le contrôleur peut être instancié normalement en 
    indiquant qu'il peut se connecter à l'instance de l'objet de modèle du template. 
    Ensuite, le contrôleur pourra envoyer les mails avec ses méthodes spécifiques.
    """
    
    key = "DummyTemplate" # Must be unique for each template
    label = "Base mail Label" # Désignation
    subject = "My dummy subject" # Template du sujet du mail
    body = "My dummy body saying : {{ dummy_var }}" # Template du message du mail
    help = None # Aide supplémentaire optionnelle utilisée dans l'administration
    historize_content = MAILINGS_HISTORIZE_CONTENT # Active/Désactive l'historisation des envois
    
    def __init__(self, context={}, passive=False, with_history=MAILINGS_WITH_HISTORY, auto_escaping=False, debug=MAILINGS_SEND_DEBUG):
        """
        :type context: dict
        :param context: (optional) Dictionnaire des variables du contexte initiale. Vide 
                        par défaut.
        
        :type passive: bool
        :param passive: (optional) Option pour ne pas effectuer la connection automatique 
                        de l'instance à son objet de modèle. Par défaut cette option est 
                        désactivée.
        
        :type with_history: dict
        :param with_history: (optional) Active l'historisation de chaque envoi de mail. 
                             Activé par défaut.
        
        :type auto_escaping: bool
        :param auto_escaping: (optional) Option d'activation de l'auto-escaping des 
                              variables appliqué par le système de templates de Django. 
                              Désactivé par défaut car les emails n'ont pas à gérer ce 
                              problème d'échappement. Généralement donc il n'est pas 
                              utile de s'occuper de cette option, elle existe uniquement 
                              par convenance et aussi pour la partie syncdb.
        
        :type debug: bool
        :param debug: (optional) Option d'activation du mode debug qui empêche tout les 
                      envois de mails. Tout les traitements sont effectués mais jamais un 
                      mail ne sera envoyé. Cette option vaut par défaut la valeur de 
                      ``settings.MAILINGS_SEND_DEBUG``. Si cette option n'existe pas dans 
                      les settings, ``False`` sera utilisé par défaut.
        """
        self.context = context
        self.passive = passive
        self.with_history = with_history
        self.auto_escaping = auto_escaping
        self.debug = debug
        
        self.passive = passive
        self._model_instance = None
        if not self.passive:
            self.connect_to_object()

    def connect_to_object(self, instance=None):
        """
        Connection de l'instance à son objet de modèle
        
        Va récupérer l'entrée en bdd du template d'après son nom clé
        
        :type instance: object `Sveetchies.django.mailings.models.Template`
        :param instance: (optional) Instance d'un modèle de template à 
                                  connecter, si il est spécifié la connection se fera 
                                  sans se soucier de la valeur de l'attribut ``BaseMailTemplate.key``. 
                                  Vide par défaut, ce qui induit une connection automatique à 
                                  l'instance d'après l'attribut ``BaseMailTemplate.key``
        """
        if not instance:
            instance = MailTemplate.objects.get(key=self.key)
        self._model_instance = instance

    def get_available_variables(self):
        """
        Méthodes d'accès à l'aide des variables
        
        Ceci est utilisé par les aides automatiques de chaque template pour donner 
        un détails du contexte disponible.
        
        :rtype: dict
        :return: Dictionnaire des noms des variables avec leur description
        """
        return self.get_variables_help()

    def get_variables_help(self):
        """
        Méthode de définition des variables
        
        À implémenter par les controleurs pour définir les aides de ses variables
        
        :rtype: dict
        :return: Dictionnaire des noms des variables avec leur description
        """
        return {}

    def get_available_tags(self):
        """
        Renvoi les noms de tags mis en avant pour ce template
        
        Ceci est utilisé par les aides automatiques de chaque template pour donner 
        un détails du contexte disponible.
        
        :rtype: tuple
        :return: Liste de tuple (key, value) à afficher, key est le contenu du premier 
                 élément du tag sans les ``{% %}``.
        """
        return (
            #('if foo', u'Condition si foo est activé.'),
        )

    def get_initial_datas(self):
        """
        Données initiales utilisées pendant le syncdb
        
        :rtype: dict
        :return: les données indéxés par leur nom d'attribut dans le modèle
        """
        return {
            "key": self.key, 
            "title": self.label, 
            "subject": self.get_raw_subject(), 
            "body": self.get_raw_body(), 
        } 

    def set_auto_escaping(self, source):
        """
        Ajoute les balises de templates du tag de désactivation de l'auto-escaping
        
        Ce tag n'est ajouté que si le contrôleur a été instancié avec l'argument 
        ``auto_escaping`` à False (comportement par défaut).
        
        :type source: string
        :param source: Contenu du template auquel ajouter le tag
        
        :rtype: string
        :return: le template avec ou sans le tag supplémentaire
        """
        if self.auto_escaping:
            return source
        # TODO: utiliser string.format()
        return "{%% autoescape off %%}%s{%% endautoescape %%}" % source

    def get_raw_subject(self):
        """
        Renvoi le template du sujet
        
        En mode passif et sans connection à l'instance de son objet de modèle, le contenu 
        est celui définit dans l'attribut statique du controleur.
        
        En revanche si l'instance est connectée, le contenu sera celui enregistré en BDD.
        
        Au final le contenu est toujours le template brut qui est à utiliser pour générer 
        le sujet final à partir du template et son contexte.
        
        :rtype: string
        :return: Template brut du sujet
        """
        if self._model_instance:
            return self.set_auto_escaping(self._model_instance.subject)
        return self.set_auto_escaping(self.subject)

    def get_raw_body(self):
        """
        Renvoi le template du message
        
        Le principe est identique à ``BaseMailTemplate.get_raw_subject()``.
        
        :rtype: string
        :return: Template brut du message
        """
        if self._model_instance:
            return self.set_auto_escaping(self._model_instance.body)
        return self.set_auto_escaping(self.body)

    def format_container(self, email, identity=None):
        """
        Méthode chargée de formater le conteneur d'une adresse email
        
        :type email: string
        :param email: Adresse email
        
        :type identity: string
        :param identity: (optional) Désignation d'identité à lier à l'adresse email 
                              de la manière ``identité <email>``. S'il n'est pas 
                              spécifié, le conteneur retourné sera juste l'adresse email 
                              tel quel.
        
        :rtype: string
        :return: Conteneur de l'adresse
        """
        if identity:
            return "%s <%s>" % (identity, email)
        return email

    def transform_sender_container(self, sender):
        """
        Traitement supplémentaire du conteneur de l'adresse d'envoi
        
        :type recipient: string
        :param recipient: Unique adresse email
        
        :rtype: string
        :return: Conteneur de l'adresse
        """
        return self.format_container(sender)

    def transform_recipient_container(self, recipient):
        """
        Passe la liste d'éléments de destinataires au formateur de récipient
        
        :type recipient: string or list
        :param recipient: Unique adresse ou liste d'adresses emails
        
        :rtype: string or list
        :return: Conteneur ou liste de conteneurs d'adresses
        """
        if isinstance(recipient, basestring):
            return self.format_container(recipient)
        return [self.format_container(item) for item in recipient]

    def set_context(self, context):
        """
        Méthode pour étendre le context en dehors de l'instanciation et sans passer par 
        les "extra_context"
        
        :type context: dict
        :param context: Dictionnaire de variables à ajouter ou écraser dans le contexte 
                        initiale donné à l'instance.
        """
        self.context.update(context)

    def get_context(self, extra_context={}):
        """
        Renvoi le contexte du template à partir des arguments clés de l'instance
        
        :type extra_context: dict
        :param extra_context: (optional) Dictionnaire de variables à écraser dans le 
                              contexte initiale donné à l'instance.
        
        :rtype: dict
        :return: Contexte
        """
        kwargs = self.context.copy()
        kwargs.update(extra_context)
        return kwargs

    def get_content(self, extra_context={}):
        """
        Formate le template de mail d'après le contexte fournit
        
        :type extra_context: dict
        :param extra_context: (optional) Dictionnaire de variables à écraser dans le 
                              contexte initiale donné à l'instance.
        
        :rtype: tuple
        :return: * Sujet du mail formaté;
                 * Message du mail formaté.
        """
        context = self.get_context(extra_context)
        subject = Template(self.get_raw_subject()).render(Context(context))
        body = Template(self.get_raw_body()).render(Context(context))
        
        return subject, body

    def send_single_mail(self, recipient_list, from_email=settings.DEFAULT_FROM_EMAIL, extra_context={}):
        """
        Envoi du message avec un même mail pour tout les destinataires
        
        Tout les destinataires verront tous l'adresse des autres destinataires dans le 
        ``To:`` du mail.
        
        :type recipient_list: string or list or tuple
        :param recipient_list: Liste des adresses à qui adresser l'email, tout les 
                               éléments seront placés dans le même ``To``. Peut être une 
                               liste d'adresse, ou directement une seule adresse (dans un 
                               string).
        
        :type from_email: string
        :param from_email: (optional) Adresse email de l'émetteur du message
        
        :type extra_context: dict
        :param extra_context: (optional) Dictionnaire de variables à écraser dans le 
                              contexte initiale donné à l'instance.
        """
        subject, body = self.get_content(extra_context)
        if isinstance(recipient_list, basestring):
            recipient_list = [recipient_list]
        
        from_email = self.transform_sender_container(from_email)
        recipient_list = self.transform_recipient_container(recipient_list)
        
        args = [subject, body, from_email, recipient_list]
        
        if not self.debug:
            send_mail(*args, fail_silently=not(settings.DEBUG))
            
        if self.with_history:
            self._historize(*args)

    def send_separate_mail(self, recipient_list, from_email=settings.DEFAULT_FROM_EMAIL, extra_context={}):
        """
        Envoi du message avec un mail pour chaque destinataire
        
        :type recipient_list: list or tuple
        :param recipient_list: Liste des adresses à qui adresser l'email. Il y aura un 
                               mail envoyé pour chaque élément de sorte qu'il n'y aura 
                               jamais qu'une seule adresse email dans le ``To``.
        
        :type from_email: string
        :param from_email: (optional) Adresse email de l'émetteur du message
        
        :type extra_context: dict
        :param extra_context: (optional) Dictionnaire de variables à écraser dans le 
                              contexte initiale donné à l'instance.
        """
        datatuple = []
        subject, body = self.get_content(extra_context)
        from_email = self.transform_sender_container(from_email)
        for item in recipient_list:
            datatuple.append((subject, body, from_email, [self.transform_recipient_container(item)]))
            
        if not self.debug:
            send_mass_mail(datatuple, fail_silently=not(settings.DEBUG))
        
        if self.with_history:
            for item in datatuple:
                self._historize(*item)

    def send_mail_managers(self, from_email=settings.DEFAULT_FROM_EMAIL, extra_context={}):
        """
        Envoi d'un mail aux managers inscrits dans ``settings.MANAGERS``
        
        Utilise ``BaseMailTemplate.send_separate_mail()`` pour envoyer tout les mails
        
        :type from_email: string
        :param from_email: (optional) Adresse email de l'émetteur du message. Par défaut 
                           l'email rempli dans ``settings.DEFAULT_FROM_EMAIL`` est 
                           utilisée.
        
        :type extra_context: dict
        :param extra_context: (optional) Dictionnaire de variables à écraser dans le 
                              contexte initiale donné à l'instance.
        """
        if self._model_instance:
            recipient_list = [self.format_container(*item) for item in settings.MANAGERS]

            self.send_separate_mail(recipient_list, from_email=from_email, extra_context=extra_context)

    def send_mail_staff(self, perm_model=None, perm_name=None, filter_func=None, from_email=settings.DEFAULT_FROM_EMAIL, extra_context={}):
        """
        Envoi d'un mail aux admins qui ont la bonne permission 
        
        Par défaut la permission "mailings.can_receive" est utilisée si aucun modèle et 
        nom de permission spécifique n'est spécifié.
        
        Utilise ``BaseMailTemplate.send_separate_mail()`` pour envoyer tout les mails
        
        :type perm_model: object `django.db.models.Model`
        :param perm_model: (optional) Modèle auquel appartient la permission. Par défaut 
                           ``Sveetchies.django.mailings.models.MailTemplate``.
        
        :type perm_name: String
        :param perm_name: (optional) Nom clé de la permission. Par défaut vaut le contenu 
                          de ``Sveetchies.django.mailings.models.RECEIVE_PERMISSION_KEY``.
        
        :type filter_func: function
        :param filter_func: (optional) Fonction qui sert à valider les utilisateurs séléctionnés 
                                comme admins. La fonction ne prends qu'un seul argument, 
                                l'objet de l'utilisateur et elle doit renvoyer un booléen 
                                confirmant ou non l'utilisateur.
        
        :type from_email: string
        :param from_email: (optional) Adresse email de l'émetteur du message. Par défaut 
                           l'email rempli dans ``settings.DEFAULT_FROM_EMAIL`` est 
                           utilisée.
        
        :type extra_context: dict
        :param extra_context: (optional) Dictionnaire de variables à écraser dans le 
                              contexte initiale donné à l'instance.
        """
        if self._model_instance:
            if not perm_model:
                perm_model = MailTemplate
            if not perm_name:
                perm_name = RECEIVE_PERMISSION_KEY
            
            queryset = get_user_queryset_from_perm(perm_model, perm_name, filter_kwargs={'is_active':True})
            recipient_list = [userObject for userObject in queryset if not filter_func or filter_func(userObject)]

            self.send_separate_mail(recipient_list, from_email=from_email, extra_context=extra_context)

    def _historize(self, subject, body, from_email, to_email):
        """
        Enregistre un historique de l'envoi
        
        :type subject: string
        :param subject: Sujet du message. Vide par défaut. Même si bien renseigné, 
                        il ne sera pas utilisé si l'attribut ``historize_content`` de 
                        l'instance vaut ``False``.
        
        :type body: string
        :param body: Contenu du message. Vide par défaut. Même si bien renseigné, 
                     il ne sera pas utilisé si l'attribut ``historize_content`` de 
                     l'instance vaut ``False``.
        
        :type from_email: string
        :param from_email: Adresse email utilisée comme émetteur.

        :type to_email: string
        :param to_email: Adresse email utilisée comme destination.
        """
        # Si to_email n'est pas un string on suppose qu'on a une liste d'email, pour 
        # lequel on crée une entrée d'historique par email
        if self._model_instance:
            if not isinstance(to_email, basestring):
                for item in to_email:
                    self._historize(subject, body, from_email, item)
            else:
                if not self.historize_content:
                    subject = body = None
                MailHistory(
                    template=self._model_instance,
                    to_email=to_email,
                    from_email=from_email,
                    subject=subject,
                    body=body
                ).save()
