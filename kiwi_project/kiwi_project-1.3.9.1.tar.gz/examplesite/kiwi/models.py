# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.cache import cache
from django.db import models

from django.contrib.auth.models import User

from Sveetchies.django.filefield import content_file_name

from kiwi import WIKIPAGE_ARCHIVED_DEFAULT
from kiwi.managers import WikipageManager, WIKI_WIKIPAGES_ALLACTIVE_MENU_CACHEKEY, WIKI_WIKIPAGES_ALLACTIVE_DICT_CACHEKEY

ATTACH_FILE_UPLOADTO = lambda x,y: content_file_name('attach/%Y/%m/%d', x, y)

class Attach(models.Model):
    """
    Fichier attachable à une page wiki
    """
    author = models.ForeignKey(User, verbose_name="Auteur")
    created = models.DateTimeField(u'date de création', auto_now_add=True)
    title = models.CharField(u'titre', max_length=120)
    archived = models.BooleanField(u'archivé', default=False, help_text=u"Un fichier archivé n'apparait pas sur le site mais reste conservé sauf si vous le supprimez complètement.")
    file = models.FileField(u'fichier', upload_to=ATTACH_FILE_UPLOADTO, max_length=255, blank=False)
    description = models.TextField(u'description', blank=True)
    is_public = models.BooleanField(u'fichier publique', default=True, help_text=u"Un fichier non publique ne sera disponible qu'aux utilisateurs authentifiés.")
    
    def __unicode__(self):
        archived = is_public = u""
        if self.archived: archived = u" (Archivé)"
        if not self.is_public: is_public = u" (Privé)"
        return "%s%s%s" % (self.title, archived, is_public)
    
    class Meta:
        verbose_name = "Fichier d'attachement"
        verbose_name_plural = "Fichiers d'attachements"

class Template(models.Model):
    """
    Label d'un template disponible pour les Wikipage
    """
    date = models.DateTimeField(u'date de création', auto_now=True)
    title = models.CharField(u'titre', max_length=100, help_text=u'Titre du label qui sera affiché dans les listes de séléctions. Ce titre est destiné aux administrateur à titre d\'indication de nature, il doit être clair.')
    path = models.CharField(u'chemin', max_length=255, help_text=u'<ins>Chemin <strong>relatif</strong> depuis un de vos répertoires de templates</ins> configurés dans vos "settings".')
    included = models.BooleanField(u'intégrable', blank=True, default=False, help_text=u"Indique un gabarit spécial qui n'est pas destiné à avoir sa propre page mais être intégré dans un autre gabarit d'une page.")

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Gabarit'
        verbose_name_plural = u'Gabarits'

class Wikipage(models.Model):
    """
    Document wiki pour les pages de textes du site
    """
    parent = models.ForeignKey('self', null=True, blank=True, related_name='child', help_text=u"Indiquez le document parent dont dépend celui-ci. Laissez vide pour mettre cette page au plus haut niveau de l'arborescence des documents. <br/>Ce paramètre n'a aucune utilité dans le cadre d'un document avec un gabarit du type document intégré, dans ce cas laissez le vide.")
    order = models.IntegerField(u'ordre', max_length=8, default=0, help_text=u"Vous pouvez optionnellement spécifier un indice numérique pour positionner cette page dans un ordre bien précis. <br/>Ce paramètre n'a aucune utilité dans le cadre d'un document avec un gabarit du type document intégré, dans ce cas laissez le à zéro.")
    active = models.BooleanField(u"activé", default=True, help_text=u"Option d'activation du document. <br/>Si elle n'est pas cochée, le document ne sera affiché nul part, même pour les gabarits du type document intégré.")
    in_sitemap = models.BooleanField(u"visible", default=True, help_text=u"Permet de désactiver l'affichage de ce document dans toute les listes de documents (plan du wiki et sommaire des sous-documents). <br/>Si vous utilisez un gabarit du type document intégré cette option est automatiquement décochée, cependant si vous changez par la suite pour un gabarit de page complète il vous faudra la réactiver manuellement pour que votre document soit accessible.")
    create_date = models.DateTimeField(u'date de création', auto_now_add=True)
    last_date = models.DateTimeField(u'dernière modification', auto_now=True)
    uri = models.CharField(u'uri', unique=True, max_length=255, help_text=u"Ceci est l'identifiant qui sert à retrouver la page du document dans le site. Il est fortement déconseillé de changer l'URI après son enregistrement, d'autres pages peuvent y faire référence.")
    author = models.ForeignKey(User, verbose_name="Auteur", editable=False)
    title = models.CharField(u'titre', max_length=255, help_text=u"Titre du document tel qu'il sera affiché en entête, dans les listes et le titre de la page du document.")
    text = models.TextField(u'texte', blank=True)
    template = models.ForeignKey(Template, verbose_name="Gabarit", max_length=255, blank=True, null=True, help_text=u'Vous pouvez séléctionner un gabarit particulier pour afficher votre document. <br/>À utiliser en connaissance de cause. N\'utilisez pas de gabarit du type "Document intégré" pour des documents du type "page complète". <br/>Et si le document utilise déjà un gabarit du type "Document intégré" n\'y touchez pas si vous ne connaissez pas ce que cela implique.')
    archived = models.BooleanField(u"archivé", default=WIKIPAGE_ARCHIVED_DEFAULT, help_text=u'Décochez cette option si vous ne souhaitez pas que vos modifications entraînent la création d\'une version d\'archive du contenu précédent.')
    attached_files = models.ManyToManyField(Attach, verbose_name="Fichiers", blank=True, help_text="Séléctionnez les fichiers que vous souhaitez attacher au document, pour transférer un nouveau fichier dans cette liste, utilisez l'icône <strong>+</strong>. <br/><br/><ins><strong>Les nouveaux fichiers ne seront pris en compte par l'éditeur que lorsque vous aurez enregistré les modifications</strong></ins>.<br/><br/>")
    display_attachs = models.BooleanField(u'listage des fichiers', default=False, help_text=u"Indique si la liste des fichiers attachés au document doit être affichée au bas du document.")
    objects = WikipageManager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('kiwi.views.wikipage.details', [self.uri])

    @models.permalink
    def get_history_url(self):
        return ('kiwi.views.version.history', [self.uri])

    def rev_number(self):
        """
        Calcul le numéro de version actuel à partir du nombre de versions 
        archivées
        """
        c = self.version.all().count()
        if c > 0:
            c += 1
        return c
    rev_number.short_description = u'numéro de version'

    def get_attachments(self, user=None):
        """
        Renvoi une liste des fichiers attachés au document, optionnellement limitée aux 
        droits d'un objet utilisateur
        """
        cache_key = "_get_attachments_cache_for_staff_%s" % str(user and user.is_staff)
        if not hasattr(self, cache_key):
            query_kwargs = {
                'archived':False,
            }
            if user and not user.is_staff:
                query_kwargs['is_public'] = True
            attachments = self.attached_files.filter(**query_kwargs).order_by('title')
            setattr(self, cache_key, attachments)
        return getattr(self, cache_key)
    
    def save(self):
        """
        Sauvegarde de l'objet
        """
        # Sauvegarde dans l'historique lors d'une édition si l'option 
        # d'archivage est activé
        if self.create_date and self.archived:
            old = Wikipage.objects.get(pk=self.id)
            Version(
                wikipage=self,
                parent=old.parent,
                order=old.order,
                active=old.active,
                in_sitemap=old.in_sitemap,
                date=old.last_date,
                uri=old.uri,
                author=old.author,
                title=old.title,
                text=old.text,
                rev_number=(self.version.all().count()+1),
                template=old.template,
            ).save()
        
        if self.template:
            # Retire le document du sitemap et navigations si il utilise un gabarit du type 
            # document intégré
            if self.template.included:
                self.in_sitemap = False
        
        super(Wikipage, self).save()
        # Nettoit le cache du menu des pages actives
        cache.delete(WIKI_WIKIPAGES_ALLACTIVE_MENU_CACHEKEY)
        cache.delete(WIKI_WIKIPAGES_ALLACTIVE_DICT_CACHEKEY)
    
    def delete(self):
        """
        Suppression de l'objet
        """
        super(Wikipage, self).delete()
        # Nettoit le cache du menu des pages actives
        cache.delete(WIKI_WIKIPAGES_ALLACTIVE_MENU_CACHEKEY)
        cache.delete(WIKI_WIKIPAGES_ALLACTIVE_DICT_CACHEKEY)

    class Meta:
        verbose_name = u'Document'
        verbose_name_plural = u'Documents'

class Version(models.Model):
    """
    Version d'historique d'une Wikipage
    """
    wikipage = models.ForeignKey(Wikipage, verbose_name="Document", related_name='version', help_text=u'Document dont est issue cette révision.')
    parent = models.ForeignKey(Wikipage, null=True, blank=True, related_name='versionchild', help_text=u'Document dont dépendait ce document pour cette révision.')
    order = models.IntegerField(u'ordre', max_length=8, default=0, help_text=u'Indice numérique de position de la page.')
    active = models.BooleanField(u"activé", default=True, help_text=u'Option d\'activation de la page.')
    in_sitemap = models.BooleanField(u"visible", default=True, help_text=u'Désactivation de l\'affichage du document dans toute les listes de documents (plan du wiki et sommaire des sous-documents).')
    date = models.DateTimeField(u'date de création', auto_now=True)
    uri = models.CharField(u'uri', max_length=255, help_text=u'Identifiant qui sert à retrouver la page du document dans le site.')
    author = models.ForeignKey(User, verbose_name="Auteur", help_text=u"L'utilisateur qui avait produit cette révision du document.")
    title = models.CharField(u'titre', max_length=255)
    text = models.TextField(u'texte', blank=True)
    template = models.ForeignKey(Template, verbose_name="Gabarit", max_length=255, blank=True, null=True, help_text=u'Gabarit spécifique d\'affichage du document.')
    rev_number = models.IntegerField(u'version', blank=False, default=0, editable=False, help_text=u'Numéro de révision du contenu du document.')

    def __unicode__(self):
        return u"%s v%s" % (self.title, self.rev_number)

    @models.permalink
    def get_absolute_url(self):
        return ('kiwi.views.version.details', [self.wikipage.uri, self.rev_number])

    @models.permalink
    def get_diff_url(self):
        return ('kiwi.views.version.diff', [self.wikipage.uri, self.rev_number])

    class Meta:
        verbose_name = u'Révision d\'un document'
        verbose_name_plural = u'Historique des révisions de documents'

#class Release(models.Model):
    #"""
    #Version globale pour tout le contenu du wiki
    #"""
    #date = models.DateTimeField(u'date de création', auto_now=True)
    #rev_number = models.IntegerField(u'numéro', blank=False, default=0, help_text=u'Numéro de la release.')
    #title = models.CharField(u'titre', max_length=255, blank=True, help_text=u'Titre optionnel')
    #pages = models.ManyToManyField(Version, editable=False)

    #def __unicode__(self):
        #return u"n°%s" % self.rev_number

    ##@models.permalink
    ##def get_absolute_url(self):
        ##return ('kiwi.views.release.details', self.rev_number)
    
    #def save(self):
        #"""
        #Sauvegarde de l'objet
        #"""
        #trigger = False
        #if not self.date:
            #trigger = True
        
        #super(Release, self).save()
        
        #if trigger and self.id:
            #for wikipageObject in Wikipage.objects.all():
                #self.pages.create(
                    #wikipage=wikipageObject,
                    #date=wikipageObject.date,
                    #order=wikipageObject.order,
                    #rev_number=(wikipageObject.version.all().count()+1),
                    #author=wikipageObject.author,
                    #title=wikipageObject.title,
                    #text=wikipageObject.text
                #)
    
    #class Meta:
        #verbose_name = u'Version globale du wiki'
        #verbose_name_plural = u'Versions globales du wiki'
