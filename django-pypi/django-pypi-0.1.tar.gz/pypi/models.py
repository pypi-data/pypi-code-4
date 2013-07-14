from django.db import models


class Package(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name


class Version(models.Model):
    package = models.ForeignKey(Package, related_name='versions')
    version = models.CharField(max_length=100)

    class Meta:
        unique_together = ('package', 'version')

    def __unicode__(self):
        return "%s %s" % (self.package, self.version)


class Release(models.Model):
    version = models.ForeignKey(Version, related_name='releases')
    has_sig = models.BooleanField()
    md5_digest = models.CharField(max_length=32)
    url = models.URLField()
    comment_text = models.TextField()
    python_version = models.CharField(max_length=6,
                                      choices=(('any', 'any'),
                                               ('source', 'source'),
                                               ('3.3', '3.3'),
                                               ('3.2', '3.2'),
                                               ('3.1', '3.1'),
                                               ('3.0', '3.0'),
                                               ('2.7', '2.7'),
                                               ('2.6', '2.6'),
                                               ('2.5', '2.5'),
                                               ('2.4', '2.4'),
                                               ('2.3', '2.3'),
                                               ('2.2', '2.2'),))
    upload_time = models.DateTimeField(null=True, blank=True)
    packagetype = models.CharField(max_length=13,
                                   choices=(('sdist', 'sdist'),
                                            ('bdist_egg', 'bdist_egg'),
                                            ('bdist_dumb', 'bdist_dumb'),
                                            ('bdist_wininst', 'bdist_wininst'),
                                            ('bdist_rpm', 'bdist_rpm'),
                                            ('bdist_msi', 'bdist_msi'),
                                            ('bdist_dmg', 'bdist_dmg'),
                                            ('bdist_wheel', 'bdist_wheel')))
    downloads = models.PositiveIntegerField()
    filename = models.CharField(max_length=100)
    size = models.PositiveIntegerField()

    class Meta:
        unique_together = ('version', 'upload_time')
        ordering = ('version', 'upload_time')
        get_latest_by = 'upload_time'

    def __unicode__(self):
        return unicode(self.version)
