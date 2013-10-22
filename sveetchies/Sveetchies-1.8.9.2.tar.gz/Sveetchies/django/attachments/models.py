# -*- coding: utf-8 -*-
from django.db import models

from django.contrib.auth.models import User

from Sveetchies.django.filefield import content_file_name
from Sveetchies.django.attachments import ATTACHMENTS_FILE_UPLOADPATH
from managers import AttachManager

ATTACHMENTS_FILE_UPLOADTO = lambda x,y: content_file_name(ATTACHMENTS_FILE_UPLOADPATH, x, y)

# TODO: Ajouter un modèle de raccourci de groupe de fichiers

class Attach(models.Model):
    """
    Fichier
    """
    author = models.ForeignKey(User, verbose_name="Auteur", related_name="attach_author")
    created = models.DateTimeField(u'date de création', auto_now_add=True)
    title = models.CharField(u'titre', max_length=120)
    archived = models.BooleanField(u'archivé', default=False, help_text=u"Un fichier archivé n'apparait pas sur le site mais reste conservé sauf si vous le supprimez complètement.")
    file = models.FileField(u'fichier', upload_to=ATTACHMENTS_FILE_UPLOADTO, max_length=255, blank=False)
    description = models.TextField(u'description', blank=True)
    is_public = models.BooleanField(u'fichier publique', default=True, help_text=u"Un fichier non publique ne sera disponible qu'aux utilisateurs authentifiés.")
    objects = AttachManager()
    
    def __unicode__(self):
        archived = is_public = u""
        if self.archived: archived = u" (Archivé)"
        if not self.is_public: is_public = u" (Privé)"
        return "%s%s%s" % (self.title, archived, is_public)
    
    class Meta:
        verbose_name = "Fichier"
        verbose_name_plural = "Fichiers"
