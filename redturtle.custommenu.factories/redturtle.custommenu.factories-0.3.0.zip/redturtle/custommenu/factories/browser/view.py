# -*- coding: utf-8 -*-

from zope.interface import implements, alsoProvides, noLongerProvides
from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from redturtle.custommenu.factories.config import ANN_CUSTOMMENU_KEY
from redturtle.custommenu.factories import custommenuMessageFactory as _
from redturtle.custommenu.factories.interfaces import ICustomMenuEnabled

class CustomizeFactoriesMenu(BrowserView):
    """View for managing custom factories menu"""

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        request.set('disable_border', True)

    enable_template = ViewPageTemplateFile('enabled.pt')

    def __call__(self):
        request = self.request
        context = self.context
        plone_utils = getToolByName(context, 'plone_utils')
        message = None
        if request.form.get("add-command",''):
            # request.response.setHeader('Content-Type','application/json')
            message = self._addMenuEntry(request.form)
            request.response.redirect(context.absolute_url()+'/@@customize-factoriesmenu')
        elif request.form.get("update-command",''):
            message = self._updateMenuEntries(request.form)
            request.response.redirect(context.absolute_url()+'/@@customize-factoriesmenu')
        elif request.form.get("delete-command",''):
            message = self._deleteMenuEntries(request.form)
            request.response.redirect(context.absolute_url()+'/@@customize-factoriesmenu')
        elif request.form.get("enable-command",''):
            self.enable()
            message = _(u"Enabled local customizations")
            request.response.redirect(context.absolute_url()+'/@@customize-factoriesmenu')            
        elif request.form.get("disable-command",''):
            self.disable()
            message = _(u"Local customizations disabled")
            request.response.redirect(context.absolute_url())            
        if message:
            if type(message)==tuple:
                message, tp = message
            else:
                tp = 'info'
            plone_utils.addPortalMessage(message, type=tp)
            return
        if self.enabled:
            return self.index()
        return self.enable_template()

    def _addMenuEntry(self, form):
        context = self.context
        
        # check not-mandatory data
        if not form.get('element-name') or not form.get('element-tales'):
            return _(u'Please, provide all required data'), 'error'
        
        extras, saved_customizations = self.getSavedCustomizations()
        saved_customizations.append(self._generateNewMenuElement(
                                        len(saved_customizations),
                                        form.get('element-id'),
                                        form.get('element-name'),
                                        form.get('element-descr'),
                                        form.get('icon-tales'),
                                        form.get('condition-tales'),
                                        form.get('element-tales'))
                                    )
        
        annotations = IAnnotations(context)
        annotations[ANN_CUSTOMMENU_KEY] = (extras, saved_customizations)
        annotations._p_changed=1
        return _(u'New entry added')

    def _updateMenuEntries(self, form):
        context = self.context
        saved_customizations = []

        for x in range(0, len(form.get('index',[]))):
            # check not-mandatory data
            if not form.get('element-name')[x] or not form.get('element-tales')[x]:
                return _(u'Please, provide all required data'), 'error'
            saved_customizations.append(
                self._generateNewMenuElement(x, form.get('element-id')[x], form.get('element-name')[x],
                                             form.get('element-descr')[x], form.get('icon-tales')[x],
                                             form.get('condition-tales')[x], form.get('element-tales')[x]))
        
        annotations = IAnnotations(context)
        annotations[ANN_CUSTOMMENU_KEY] = ({'inherit': form.get('inherit',False)}, saved_customizations)
        annotations._p_changed=1
        return _(u'Customizations updated')

    def _generateNewMenuElement(self, index, id, name, descr, icon, condition, element):
        return {'index': index,
                'element-id': id,
                'element-name': name,
                'element-descr': descr,
                'icon-tales': icon,
                'condition-tales': condition,
                'element-tales': element,
                }

    def _deleteMenuEntries(self, form):
        context = self.context
        extras, saved_customizations = self.getSavedCustomizations()

        to_delete = form.get('delete',[])
        if not to_delete:
            return _(u'Please, select at least one entry to be deleted'), 'error'
        saved_customizations = [x for x in saved_customizations if x['index'] not in to_delete]
        self._reindex(saved_customizations)
        
        annotations = IAnnotations(context)
        annotations[ANN_CUSTOMMENU_KEY] = (extras, saved_customizations)
        annotations._p_changed=1
        return _(u'Customizations removed')

    def enable(self):
        """Enabled local customization, adding the annotation structure"""
        context = self.context
        annotations = IAnnotations(context)
        alsoProvides(context, ICustomMenuEnabled)
        context.reindexObject('object_provides')
        annotations[ANN_CUSTOMMENU_KEY] = self.getSavedCustomizations()
    
    def disable(self):
        """Disable local customization, removing annotation data"""
        context = self.context
        annotations = IAnnotations(context)
        try:
            del annotations[ANN_CUSTOMMENU_KEY]
            noLongerProvides(context, ICustomMenuEnabled)
            context.reindexObject('object_provides')
        except KeyError:
            pass

    @property
    def enabled(self):
        context = self.context
        annotations = IAnnotations(context)
        return annotations.has_key(ANN_CUSTOMMENU_KEY)

    def getSavedCustomizations(self):
        context = self.context
        annotations = IAnnotations(context)
        if annotations.has_key(ANN_CUSTOMMENU_KEY):
            return annotations[ANN_CUSTOMMENU_KEY]
        return ({'inherit': True}, [])

    @property
    def listCustomizations(self):
        """Return all saved customization to be shown in the template"""
        return self.getSavedCustomizations()[1]
    
    @property
    def inherit(self):
        return self.getSavedCustomizations()[0]['inherit']

    @property
    def onSiteRoot(self):
        """Check if the context is the Plone site"""
        # BBB: can leave to problems with subsites? To be tested
        return IPloneSiteRoot.providedBy(self.context)
        
    def _reindex(self, customizations_list):
        """Fix all index inside a customizations structure.
        @return: the customization list itself
        """
        for x in range(0, len(customizations_list)):
            customizations_list[x]['index'] = x
        return customizations_list
