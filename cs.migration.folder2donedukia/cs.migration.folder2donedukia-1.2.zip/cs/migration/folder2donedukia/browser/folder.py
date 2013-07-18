from Acquisition import aq_inner, aq_parent
from Products.Five.browser import BrowserView

class Folder2DonEdukia(BrowserView):
    def __call__(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        default_page_id = context.getProperty('default_page', None)
        if default_page_id is not None:
            elem = getattr(context, default_page_id, None)
            if elem is not None:
                new_id = parent.invokeFactory(id=parent.generateUniqueId(),
                                              type_name='DonEdukia',
                                              title=elem.Title(),
                                              description=elem.Description(),
                                              text=elem.getText(),
                                              )
        else:
                new_id = parent.invokeFactory(id=parent.generateUniqueId(),
                                              type_name='DonEdukia',
                                              title=context.Title(),
                                              description=context.Description(),
                                              ) 
        new_obj = getattr(parent, new_id)
        new_obj._renameAfterCreation()
           
        for lang, props in context.getTranslations().items():
            obj = props[0]
            if obj.UID() != context.UID():
                obj.removeTranslationReference(context)
                context.removeTranslationReference(obj)
                new_obj.addTranslationReference(obj)

        cp_data = context.manage_copyObjects([i.getId for i in context.getFolderContents()])
        new_obj.manage_pasteObjects(cp_data)
        parent.manage_delObjects(context.getId())
        new_obj._renameAfterCreation()
        return self.request.response.redirect(new_obj.absolute_url())
