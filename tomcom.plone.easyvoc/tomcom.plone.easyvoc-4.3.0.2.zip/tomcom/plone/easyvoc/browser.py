from tomcom.browser.public import *

class IEasyVoc(Interface):

    def set_config(self):
        """ """

    def get_config(self):
        """ """

    def set(self):
        """ """

    def get(self,storage_key):
        """ """

    def get_as_dict_value_as_key(self,storage_key):
        """ """

    def get_value(self,storage_key,key):
        """ """

class Browser(BrowserView):

    implements(IEasyVoc)

    _storage_key='_easyvoc'

    def set_config(self):
        """ """
        context=self.context

        context.getBrowser('tpcheck').auth_easyvoc_manage()

        form=context.REQUEST.form

        message=context.getAdapter('message')
        _=context.getAdapter('translate')
        annotation=context.getAdapter('annotation')

        annotation[self._storage_key]=dict(form)

        msgstr=_(msgid='Changes saved.', domain='plone', default='Changes saved.')
        message(msgstr)
        return context.REQUEST.RESPONSE.redirect(context.REQUEST['HTTP_REFERER'])


    def get_config(self):

        context=self.context
        context.getBrowser('tpcheck').auth_easyvoc_manage()

        context=self.context
        portal=context.getAdapter('portal')()
        annotation=portal.getAdapter('annotation')
        return annotation.get(self._storage_key,{})

    def _get_tn(self,storage_key=''):

        context=self.context

        if not storage_key:
            storage_key=self._get_storage_key()

        data=self._get_data(storage_key)
        counter=data.get('counter',0)
        counter+=1
        data['counter']=counter
        self._set_data(data,storage_key)
        return counter

    def _get_data(self,storage_key):

        context=self.context
        portal=context.getAdapter('portal')()
        annotation=portal.getAdapter('annotation')
        return annotation.get(storage_key,{})

    def _set_data(self,data,storage_key=''):

        context=self.context
        portal=context.getAdapter('portal')()
        annotation=portal.getAdapter('annotation')
        if not storage_key:
            storage_key=self._get_storage_key()
        annotation[storage_key]=data

    def get_list_as_string(self):

        context=self.context

        context.getBrowser('tpcheck').auth_manage_portal()

        data=self._get_data(self._get_storage_key())

        print data
        return '\r\n'.join(data.get('list_',''))

    def get_mapping_reverse(self,data):

        dict_={}
        for k,v in data.get('mapping',{}).items():
            dict_[v]=k
        return dict_

    def get(self,storage_key):

        context=self.context
        context.getBrowser('tpcheck').auth_view()

        _=context.getAdapter('translate')
        data=self._get_data(storage_key)
        mapping=self.get_mapping_reverse(data)

        list_=[]
        msgstr=_(msgid='Please select', domain='plone', default='Please select')
        list_.append(('',msgstr))

        for item in data.get('list_',[]):
            list_.append((str(mapping[item]),item))



        return list_

    def get_as_dict_value_as_key(self,storage_key):

        dict_=OrderedDict()
        for k,v in self.get(storage_key):
            dict_[v]=k
        return dict_

    def get_value(self,storage_key,key):

        context=self.context
        context.getBrowser('tpcheck').auth_view()

        data=self._get_data(storage_key)
        try:
            key=int(key)
        except:
            return key
        return data.get('mapping',{}).get(int(key),key)

    def _get_storage_key(self):

        context=self.context
        return context.REQUEST.form.get('key','')

    def set(self):
        """ """
        context=self.context
        context.getBrowser('tpcheck').auth_easyvoc_manage()

        form=context.REQUEST.form
        data=self._get_data(self._get_storage_key())
        message=context.getAdapter('message')
        portal=context.getAdapter('portal')()
        _=context.getAdapter('translate')

        list_=[item.strip() for item in form.get(self._get_storage_key(),'').split('\n') if item.strip()]

        if not data.has_key('mapping'):
            data['mapping']={}

        mappingReverse=self.get_mapping_reverse(data)
        for item in list_:
            if not mappingReverse.has_key(item):
                data['mapping'][self._get_tn()]=item

        mapping=dict(data['mapping'])
        data=self._get_data(self._get_storage_key())
        data['list_']=list_
        data['mapping']=mapping

        change_from=form.get('change_from','')
        change_to=form.get('change_to','')
        if change_from and change_to:

            if change_to in data['mapping'].values():
                msgstr=_(msgid='cannot_rename_key_not_exist', default='Entry can\'t be renamed to this value. It exists as an old key value pair.')
                message(msgstr)
                return context.REQUEST.RESPONSE.redirect(context.REQUEST['HTTP_REFERER'])

            change_from=int(change_from)
            old=data['mapping'][change_from]

            data['list_'][data['list_'].index(old)]=change_to

            data['mapping'][change_from]=change_to

        self._set_data(data)

        msgstr=_(msgid='Changes saved.', domain='plone', default='Changes saved.')
        message(msgstr)

        return context.REQUEST.RESPONSE.redirect(portal.absolute_url()+'/configure_easyvoc')