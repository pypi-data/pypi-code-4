from Products.Five.browser import BrowserView
from collective.transmogrifier.transmogrifier import configuration_registry
from collective.transmogrifier.transmogrifier import Transmogrifier


class Import(BrowserView):

    def __call__(self):
        pipeline_id = 'import-chm-terms'
        pipelines = configuration_registry.listConfigurationIds()
        if pipeline_id is not None and pipeline_id in pipelines:
            transmogrifier = Transmogrifier(self.context)
            transmogrifier(pipeline_id)
            pipeline = configuration_registry.getConfiguration(pipeline_id)
            return 'done'

        return 'invalid pipeline'
