# -*- coding: utf-8 -*-

import copy

from flask import request, redirect
from flask import render_template
from flask.views import MethodView


class SingleObjectMixin(object):
    model = None
    queryset = None
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'pk'
    context_object_name = 'object'

    def get_object(self, *args, **kwargs):
        queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = kwargs.get(self.pk_url_kwarg, None)
        slug = kwargs.get(self.slug_url_kwarg, None)

        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        else:
            raise AttributeError(u"Generic detail view %s must be called with "
                                 u"either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            obj = queryset.get()
        except self.model.DoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': self.model.__name__})
        return obj

    def get_queryset(self):
        # XXX: Nevyzere nam to pamet???
        return copy.copy(self.queryset)

    def get_context_object_name(self):
        return self.context_object_name

    def get_slug_field(self):
        return self.slug_field

    def get_context(self, *args, **kwargs):
        context = kwargs
        context_object_name = self.get_context_object_name()
        if context_object_name:
            context[context_object_name] = self.object
        return context


class TemplateMixin(object):
    template = ''

    def get_template_name(self):
        return self.template

    def get_context(self, *args, **kwargs):
        context = kwargs
        return context

    def render_template(self, *args, **kwargs):
        context = self.get_context(*args, **kwargs)
        return render_template(self.get_template_name(), **context)


class FormMixin(object):
    form_class = None  # Form class
    success_url = None

    def get_form_class(self):
        return self.form_class

    def get_form(self, form_class, instance=None):
        return form_class(request.form, instance)

    def get_success_url(self):
        if self.success_url:
            url = self.success_url
        else:
            raise ValueError('No URL to redirect to.  Either provide a url or define a get_absolute_url method on the Model.')  # FIXME: Je vhodne vyvolat ValueError?

        return url

    def form_valid(self, form, *args, **kwargs):
        return redirect(self.get_success_url())

    def form_invalid(self, form, *args, **kwargs):
        kwargs['form'] = form
        return self.render_template(*args, **kwargs)


class View(TemplateMixin, MethodView):
    """
    Obecny pohled.
    """
    def get(self, *args, **kwargs):
        return self.render_template(*args, **kwargs)


class DetailView(SingleObjectMixin, TemplateMixin, MethodView):
    def get(self, *args, **kwargs):
        self.object = self.get_object(*args, **kwargs)
        return self.render_template(*args, **kwargs)


class FormView(FormMixin, TemplateMixin, MethodView):
    def get(self, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        return self.render_template(form=form, *args, **kwargs)

    def post(self, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.validate():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class UpdateView(SingleObjectMixin, FormMixin, TemplateMixin, MethodView):
    """
    Generic view for edit object.
    """
    def get(self, *args, **kwargs):
        self.object = self.get_object(*args, **kwargs)
        form_class = self.get_form_class()
        form = self.get_form(form_class, self.object)

        return self.render_template(form=form, *args, **kwargs)

    def post(self, *args, **kwargs):
        self.object = self.get_object(*args, **kwargs)
        form_class = self.get_form_class()
        form = self.get_form(form_class, self.object)

        if form.validate():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
