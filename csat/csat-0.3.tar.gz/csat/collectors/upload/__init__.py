from csat.acquisition import base


__version__ = '0.1.0'


class UploadCollector(base.ConfiguratorBase):

    name = 'File upload slot'
    key = 'upload'
    version = __version__

    def get_form(self):
        from . import forms
        return forms.ConfigForm

    def get_model(self):
        from . import models
        return models.UploadConfig

    def get_command(self, model):
        pass

    def run(self, request, model, remote):
        model.create_postback_url()


upload_collector = UploadCollector()
