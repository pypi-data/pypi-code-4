from Acquisition import aq_inner, aq_parent
from Products.Five.browser import BrowserView

class Folder2DonEdukia(BrowserView):
    def __call__(self, code=0):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        default_page_id = context.getProperty('default_page', None)
        if default_page_id is not None:
            elem = getattr(context, default_page_id, None)
            if elem is not None:
                try:
                    new_id = parent.invokeFactory(id=parent.generateUniqueId(),
                                              type_name='DonEdukia',
                                              title=elem.Title(),
                                              description=elem.Description(),
                                              text=elem.getText(),
                                              )
                except Exception,e:
                    from logging import getLogger
                    log = getLogger('cs.migration.folder2donedukia')
                    log.info(e)
                    log.info(context.absolute_url())
                    return 'XXXXX %s' % context.absolute_url()
                    
            else:
                from logging import getLogger
                log = getLogger('cs.migration.folder2donedukia')
                log.info('default_page does not exist: %s %s' % (context.absolute_url(), default_page_id))
                try:
                    new_id = parent.invokeFactory(id=parent.generateUniqueId(),
                                              type_name='DonEdukia',
                                              title=context.Title(),
                                              description=context.Description(),
                                              )
                except Exception,e:
                    from logging import getLogger
                    log = getLogger('cs.migration.folder2donedukia')
                    log.info(e)
                    log.info(context.absolute_url())
                    return 'XXXXX %s' % context.absolute_url()
        else:
            try:
                new_id = parent.invokeFactory(id=parent.generateUniqueId(),
                                          type_name='DonEdukia',
                                          title=context.Title(),
                                          description=context.Description(),
                                          ) 
            except Exception,e:
                    from logging import getLogger
                    log = getLogger('cs.migration.folder2donedukia')
                    log.info(e)
                    log.info(context.absolute_url())
                    return 'XXXXX %s' % context.absolute_url()

        new_obj = getattr(parent, new_id)
        #new_obj._renameAfterCreation()
           
        try:
            # Try with translations
            for lang, props in context.getTranslations().items():
                obj = props[0]
                if obj.UID() != context.UID():
                    obj.removeTranslationReference(context)
                    context.removeTranslationReference(obj)
                    new_obj.addTranslationReference(obj)
        except:
            pass
        
        cp_data = context.manage_copyObjects([i.getId for i in context.getFolderContents()])
        new_obj.manage_pasteObjects(cp_data)
        parent.manage_delObjects(context.getId())
        new_obj._renameAfterCreation()
        if not code:
            return self.request.response.redirect(new_obj.absolute_url())
        else:
            return new_obj.absolute_url()

class Doc2DonEdukia(BrowserView):
    def __call__(self, code=0):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        new_id = parent.invokeFactory(id=parent.generateUniqueId(),
                                      type_name='DonEdukia',
                                      title=context.Title(),
                                      description=context.Description(),
                                      text=context.getText(),
                                      ) 
        new_obj = getattr(parent, new_id)
        new_obj._renameAfterCreation()
        try:
            # Try with translations
            for lang, props in context.getTranslations().items():
                obj = props[0]
                if obj.UID() != context.UID():
                    obj.removeTranslationReference(context)
                    context.removeTranslationReference(obj)
                    new_obj.addTranslationReference(obj)
        except:
            pass
        
        new_obj._renameAfterCreation()
        if not code:
            return self.request.response.redirect(new_obj.absolute_url())
        else:
            return new_obj.absolute_url()

