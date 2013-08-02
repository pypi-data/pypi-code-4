# coding=utf-8
from renderer import FormRenderer
from preprocessors.bootstrap import append_preprocessor, prepend_preprocessor


class BootstrapFormRenderer(FormRenderer):
    template = 'form-renderer/bootstrap.html'

    def __init__(self, form, request=None, form_id=None, csrf_token=None, template=None):
        FormRenderer.__init__(self, form, request, form_id, csrf_token, template)
        if self.extra_context_dict is None:
            self.extra_context_dict = {}

        self.pre_processors.append(append_preprocessor)
        self.pre_processors.append(prepend_preprocessor)

        self.extra_context_dict['button_color'] = 'blue'
        self.extra_context_dict['layout'] = 'horizontal'

    @property
    def button_color(self):
        return self.extra_context_dict.get('button_color')

    @button_color.setter
    def button_color(self, value):
        self.extra_context_dict['button_color'] = value

    @property
    def layout(self):
        return self.extra_context_dict.get('layout')

    @layout.setter
    def layout(self, value):
        self.extra_context_dict['layout'] = value

