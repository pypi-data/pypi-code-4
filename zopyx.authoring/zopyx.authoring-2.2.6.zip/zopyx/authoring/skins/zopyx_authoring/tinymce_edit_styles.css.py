# Redirect and include TinyMCE edit styles only for content inside the 
# the authoring environment


try: 
    project = context.getAuthoringProject()
    return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/tinymce_edit_styles2.css')
except AttributeError:
    return '/* */'

