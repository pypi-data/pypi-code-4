import os.path

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from plone.app.z3cform import templates

path = lambda p: os.path.join(os.path.dirname(__file__), 'templates', p)


class PlainMainMacros(templates.Macros):
    """\
    Trying to make life easier for general testing
    """

    index = ViewPageTemplateFile(path('plain-main-macros.pt'))


class PloneMainMacros(templates.Macros):
    """\
    The main macros, including templates.
    """

    index = ViewPageTemplateFile(path('plone-main-macros.pt'))


class PloneZ3cformMacros(templates.Macros):
    """
    Extension to the plone.z3cform macros.

    Implements recursive rendering of fieldsets and buttons for them.

    As the macro defined by the template here is a copy of the one found
    in plone.app.z3cform, the functionality is identical except for the
    rendering of fieldsets and buttons.  While it should not interfere
    with the standard macro that is shipped, but due to the experimental
    nature of this macro, how other forms may introduce their own highly
    customized macros, or the installed plone.app.z3cform may have an
    updated version of this template, the configure.zcml entry for this
    class is not defined.  Users of this macro should have the
    appropriate definition added to their configure.zcml that makes it
    specific to their content or layer so that it remains completely
    isolated and limits interferences with other forms and views.

    An example: if the specialized form is made available on top of the
    root portal object, a layer MUST be defined and used, with the zcml
    tag added::

        <browser:page
            name="ploneform-macros"
            for="Products.CMFPlone.interfaces.IPloneSiteRoot"
            layer=".interfaces.ICustomMacroLayer"
            class="pmr2.z3cform.templates.Macros"
            allowed_interface="zope.interface.common.mapping.IItemMapping"
            permission="zope.Public"
            />

    The layer interface has to inherit from z3c.form.interfaces so that
    the interface resolution order works.  While IPloneFormLayer may be
    better, it will cause the unintended effect of invoking the Plone
    layout all the time within the target views::

        from z3c.form.interfaces import IFormLayer

        class ICustomMacroLayer(IFormLayer):
            pass

    Since that layer is specific to this form, the layer can be manually
    assigned like so within the update method for the form.

        import zope.interface
        from z3c.form import form
        from plone.z3cform.fieldsets import extensible

        from .interfaces import ICustomMacroLayer

        class SpecialForm(form.PostForm, extensible.ExtensibleForm):
            def update(self):
                zope.interface.alsoProvides(self.request, ICustomMacroLayer)
                super(SpecialForm, self).update()

    This will then ensure when the template is called in the render, the
    ploneform-macros macro will resolve to this customized one to allow
    the nested fieldsets with buttons to be rendered as intended.
    """

    index = ViewPageTemplateFile(path('plone-z3cform-macros-ex.pt'))
