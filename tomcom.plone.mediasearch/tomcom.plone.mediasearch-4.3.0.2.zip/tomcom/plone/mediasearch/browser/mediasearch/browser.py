#!/usr/bin/python
# -*- coding: utf-8 -*-

from tomcom.browser.public import *

class IMediaSearch(Interface):

    def paste(self):
        """ """

    def search(self):
        """ """

    def get_languages(self):
        """ """

    def get_portal_types(self):
        """ """

    def get_parents(self):
        """ """

    def unlock(self):
        """ """

class Browser(BrowserView):

    implements(IMediaSearch)

    def paste(self):
        """ """
        context=self.context

        context.getBrowser('tpcheck').auth_copy_or_move()

        portal=context.getAdapter('portal')()
        form=context.REQUEST.form
        rc=context.getAdapter('rc')()
        uid=form.get('uid')
        message=context.getAdapter('message')

        current=rc.lookupObject(uid)
        parent_current=current.aq_parent
        if form.get('input_type')=='move':
            cp=parent_current.manage_cutObjects(ids=[current.getId()])
        else:
            cp=parent_current.manage_copyObjects(ids=[current.getId()])

        context.manage_pasteObjects(cp)

        message('Changes saved.')

        return context.REQUEST.RESPONSE.redirect(portal.absolute_url()+'/mediasearch_view')

    def search(self):
        """ """
        context=self.context

        form=context.REQUEST.form
        pc=context.getAdapter('pc')()

        query={}

        if form.get('portal_type'):
            portal_type=form.get('portal_type')
        else:
            portal_type=['Image','File']
        query['portal_type']=portal_type

        if form.get('SearchableText',''):
            string_=form.get('SearchableText','')
            if not string_.endswith('*'):
                string_+='*'
            query['SearchableText']=string_

        return pc(query)

    def get_languages(self):

        context=self.context

        list_=context.getAdapter('supportedlanguages')()
        list_.insert(0,('all','Show all'))
        return list_

    def get_portal_types(self):

        context=self.context
        _=context.getAdapter('translate')

        list_=[]
        list_.append(('',_(msgid='Show all',domain='mediasearch')))
        list_.append(('Image',_('Image')))
        list_.append(('File',_('File')))
        return list_

    def get_parents(self):

        context=self.context
        parent=context
        list_=[]
        while parent.portal_type!='Plone Site':
            list_.append(parent)
            parent=parent.aq_parent

        list_.append(parent)

        list_.reverse()

        return list_

    def unlock(self):
        """ """
        context=self.context
        form=context.REQUEST.form
        rc=context.getAdapter('rc')()
        object_=rc.lookupObject(form.get('uid',None))

        lock_info = object_.getBrowser('plone_lock_info')
        if lock_info is not None and lock_info.is_locked():
            object_.getBrowser('plone_lock_operations').force_unlock()
