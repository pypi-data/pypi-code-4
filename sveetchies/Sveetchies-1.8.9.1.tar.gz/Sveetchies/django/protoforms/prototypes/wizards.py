# -*- coding: utf-8 -*-
from django.contrib.formtools.wizard import FormWizard
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

class BaseWizard(FormWizard):
    """
    Wizard du formulaire en deux étapes
    """
    proto_wizard_form_name = "base"
    proto_wizard_form_template = "protoforms/%s/form.html"
    proto_wizard_done_url_name = "protoforms-%s-form-finished"
    
    def __call__(self, request, *args, **kwargs):
        self.requestObject = request
        return super(BaseWizard, self).__call__(request, *args, **kwargs)
        
    def get_form(self, step, data=None, datafiles=None):
        return self.form_list[step](self.requestObject, data, datafiles, prefix=self.prefix_for_step(step), initial=self.initial.get(step, None))
        
    def get_template(self, step):
        """
        Par défaut utilise le même template pour toute les étapes d'un même formulaire
        """
        return self.proto_wizard_form_template % self.proto_wizard_form_name
    
    def done(self, request, form_list):
        return HttpResponseRedirect( reverse(self.proto_wizard_done_url_name%self.proto_wizard_form_name) )
