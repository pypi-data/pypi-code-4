from five import grok
from plone.app.layout.navigation.interfaces import INavigationRoot
from collective.transmogrifier.transmogrifier import Transmogrifier
from zope.site.hooks import getSite
from plone.memoize import ram
import logging

class ImportForm(grok.View):
	""" Form for Import
	"""

	grok.context(INavigationRoot)
	grok.name('import')
	grok.require('wasgehtengine.Import')
	
	logger = logging.getLogger('importform')

	def update(self):
		pass

	def __call__(self):

		form = self.request.form
	
		importVenuesButton = form.get('form.button.import-venues') is not None
		importEventsButton = form.get('form.button.import-events') is not None
		
		venue_import_config = form.get('osm-import-configfile')
		event_import_dir = form.get('event-import-definitions-dir')		

		if(self.request.get('REQUEST_METHOD', 'GET').upper() == 'POST'):
			transmogrifier = Transmogrifier(getSite())

			if importVenuesButton:
				self.logger.info("Importing venues...")
				transmogrifier("osm-venue-import",
							osmimportdefinitionssource=dict(file=venue_import_config))

			elif importEventsButton:
				self.logger.info("Importing events...")
				transmogrifier("event-import", eventimportdefinitionssource=dict(directory=event_import_dir))
				
			# clear all cached values 
			ram.global_cache.invalidateAll()

		return super(ImportForm, self).__call__()
