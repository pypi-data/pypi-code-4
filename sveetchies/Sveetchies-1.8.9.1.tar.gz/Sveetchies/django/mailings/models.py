# -*- coding: utf-8 -*-
"""
Modèles de données
"""
from django.db import models

RECEIVE_PERMISSION_KEY = "can_receive"

class Template(models.Model):
    """
    Template de mail
    """
    created = models.DateTimeField(u'date de création', auto_now_add=True)
    modified = models.DateTimeField(u'date de dernière modification', auto_now=True)
    key = models.SlugField(u'clé', max_length=50, unique=True, blank=False, help_text=u"Une clé d\'identification UNIQUE servant aux applications qui l'utilisent, ne pas modifier.")
    title = models.CharField(u'désignation', max_length=100, blank=False, help_text=u"Titre de désignation uniquement visible dans l'administration")
    subject = models.CharField(u'sujet', max_length=255, blank=False, help_text=u"Sujet du mail, peut contenir des variables parmi celles disponibles.")
    body = models.TextField(u'objet', blank=False, help_text=u"Contenu du message du mail, reportez-vous à l'aide pour plus de détails..")
    
    def __unicode__(self):
        return self.title
        
    class Meta:
        verbose_name = 'Template de mail'
        verbose_name_plural = 'Templates de mails'
        permissions = (
            (RECEIVE_PERMISSION_KEY, "Can Receive Staff emails"),
        )

class History(models.Model):
    """
    Historique de mail envoyé
    """
    sended = models.DateTimeField(u'date d\'envoi', auto_now_add=True)
    template = models.ForeignKey(Template, blank=False, help_text=u"Template utilisé pour générer le mail.")
    to_email = models.CharField(u'Email de réception', max_length=255, blank=False, help_text=u"L'adresse email utilisée pour le destinataire du message.")
    from_email = models.CharField(u'Email d\'émission', max_length=255, blank=False, help_text=u"L'adresse email utilisée pour l'envoi du message.")
    subject = models.CharField(u'sujet', max_length=255, blank=True, null=True, help_text=u"Sujet du mail tel qu'il a été envoyé. Vide si l'application a désactivé l'enregistrement du contenu (par raison de sécurité ou confidentialité).")
    body = models.TextField(u'objet', blank=True, null=True, help_text=u"Objet du mail tel qu'il a été envoyé. Vide si l'application a désactivé l'enregistrement du contenu (par raison de sécurité ou confidentialité).")
    
    def __unicode__(self):
        return self.template.title
        
    class Meta:
        verbose_name = 'Historique d\'envoi'
        verbose_name_plural = 'Historiques d\'envois'
