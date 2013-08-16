__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

from django.db import models
from publication import Publication

class List(models.Model):
	class Meta:
		app_label = 'publications'
		ordering = ('list',)
		verbose_name_plural = 'Publication lists'

	list = models.CharField(max_length=128)
	description = models.CharField(max_length=128)
	publications = models.ManyToManyField(Publication)

	def __unicode__(self):
		return self.list
