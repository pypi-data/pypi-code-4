# -*- coding: utf-8 -*-

'''Provides an abstract base class for creating deform views in Pyramid.'''

from __future__ import (absolute_import, division, print_function,
    unicode_literals)
from itertools import count
from pyramid_deform import CSRFSchema
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
import colander as c
import deform as d
import peppercorn
from . import button, translator, _


class BaseDeformView(object):
    '''An abstract base class (ABC) for Pyramid views that use deform.
    The workflow is divided into several methods so you can change details
    easily in subclasses.

    Subclasses must provide at least:

    * a static *schema*. (This should subclass pyramid_deform's CSRFSchema.)
    * one or more view methods that use the methods in this ABC, especially
      *_deform_workflow()* or *_colander_workflow()*.

    Example usage::

        from pyramid_deform import CSRFSchema
        from deform_bootstrap_extra.pyramid.views import BaseDeformView

        class InvitationView(BaseDeformView):
            formid = 'invitation_form'
            button_text = _("Send invitations to the above users")
            button_icon = 'icon-envelope icon-white'
            schema = MyInvitationSchema  # a CSRFSchema subclass

            @view_config(name='invite-users',
                         renderer='myapp:templates/invite-users.genshi')
            def invite_users(self):
                return self._deform_workflow()

            def _valid(self, form, controls):
                """The form validates, so now we send out the invitations,
                set up a flash message and redirect to the home page.
                """
                (...)

    If you want to do something with the POSTed data *before* validation,
    just implement this method in your subclass::

        def _preprocess_controls(self, controls):
    '''
    button_text = _("Submit")
    button_icon = None
    formid = 'form'
    bootstrap_form_style = 'form-horizontal'

    def __init__(self, context, request):
        '''Sets ``status`` to the request method. Later, ``status``
        becomes 'valid' or 'invalid'.
        '''
        self.context = context
        self.request = request
        self.status = request.method

    def _get_buttons(self):
        '''Returns the buttons tuple for instantiating the form.
        If this doesn't do what you want, override this method!
        '''
        return [button(self.button_text, icon=self.button_icon)]

    @reify
    def schema_instance(self):
        '''Give subclasses a chance to mutate the schema. Example::

            @reify
            def schema_instance(self):
                return self.schema().bind(now=datetime.utcnow())

        The default implementation binds the request for CSRF protection.
        '''
        return self.schema().bind(request=self.request)

    def _get_form(self, schema=None, action='', formid=None, buttons=None,
                  bootstrap_form_style=None):
        '''When there is more than one Deform form per page, forms must use
        the same *counter* to generate unique input ids. So we create the
        variable ``request.deform_field_counter``.
        '''
        if not hasattr(self.request, 'deform_field_counter'):
            self.request.deform_field_counter = count()
        return d.Form(schema or self.schema_instance, action=action,
            buttons=buttons or self._get_buttons(),
            counter=self.request.deform_field_counter,
            formid=formid or self.formid,
            bootstrap_form_style=bootstrap_form_style or
            self.bootstrap_form_style)

    CSRF_ERROR = _("You do not pass our CSRF protection. "
        "Maybe your session expired? In any case, you must reload "
        "that page (and probably fill out the form again). Sorry...")

    def _check_csrf(self, exception):
        '''This is called when there is a validation error. If the schema
        being validated is an instance of CSRFSchema, check the posted
        CSRF token, and if there is a problem, raise HTTPForbidden.

        If we didn't do this, the form would be redisplayed with an error
        message at the top, but the user would have no idea what is going on,
        because the CSRF token is in a hidden field.
        '''
        # if issubclass(self.schema, CSRFSchema) and \
        if isinstance(exception.error.node, CSRFSchema) and \
            self.request.session.get_csrf_token() != \
                (exception.cstruct or self.request.POST).get('csrf_token'):
            raise HTTPForbidden(translator(self.CSRF_ERROR))

    def _template_dict(self, form=None, controls=None, **k):
        '''Override this method to fill in the dictionary that is returned
        to the template. This method is called in all 3 scenarios:
        initial GET, invalid POST and validated POST. If you need to know
        which situation you're in, check ``self.status``.

        By default, the returned dict will contain a rendered ``form``.
        '''
        form = form or self._get_form()
        if isinstance(form, d.Form):
            form = form.render(controls) if controls else form.render()
        else:  # form must be a ValidationFailure exception
            form = form.render()
        return dict(form=form, **k)

    def _preprocess_controls(self, controls):
        '''If you'd like to do something with the POSTed data *before*
        validation, just override this method in your subclass.
        '''
        return controls

    def _deform_workflow(self, controls=None):
        '''Call this from your view. This performs the whole deform validation
        step (using the other methods in this abstract base class)
        and returns the appropriate dictionary for your template.
        '''
        if self.request.method == 'POST':
            return self._post(self._get_form(), controls=controls)
        else:
            return self._get(self._get_form())

    def _get(self, form):
        '''You may override this method in subclasses to do something special
        when the request method is GET.
        '''
        return self._template_dict(form=form)

    def _post(self, form, controls=None):
        '''You may override this method in subclasses to do something special
        when the request method is POST.
        '''
        controls = peppercorn.parse(controls or self.request.POST.items())
        controls = self._preprocess_controls(controls)
        try:
            appstruct = form.validate_pstruct(controls)
        except d.ValidationFailure as e:
            self.status = 'invalid'
            return self._invalid(e, controls)
        else:
            self.status = 'valid'
            appstruct.pop('csrf_token', None)  # Discard the CSRF token
            return self._valid(form=form, controls=appstruct)

    def _invalid(self, exception, controls):
        '''Override this to change what happens upon ValidationFailure.
        By default, we raise if there is a CSRF problem, so the user will
        know what's up. Otherwise, we simply redisplay the form.
        '''
        self._check_csrf(exception)
        return self._template_dict(form=exception)

    def _valid(self, form, controls):
        '''This is called after form validation. You may override this method
        to change the response at the end of the view workflow.
        '''
        raise NotImplementedError(
            "You need to    def _valid(self, form, controls):")

    def _colander_workflow(self, controls=None):
        '''Especially in AJAX views, you may skip Deform and use just colander
        for validation, returning a dictionary of errors to be displayed
        next to the form fields.
        TODO: Test
        '''
        controls = controls or self.request.POST.items()
        try:
            appstruct = self._get_schema().deserialize(controls)
        except c.Invalid as e:
            try:
                self._check_csrf(controls)
            except HTTPForbidden as e:
                return dict(errors={'': e.args[0]})
            else:
                return dict(errors=e.asdict2() if hasattr(e, 'asdict2')
                    else e.asdict())
        else:
            # appstruct.pop('csrf_token', None)  # Discard the CSRF token
            return appstruct
