from django.conf.urls.defaults import url, patterns
from djinn_forms.views.fileupload import UploadView
from django.views.decorators.csrf import csrf_exempt


urlpatterns = patterns(
    "",
    
    url(r'^fileupload$',
        csrf_exempt(UploadView.as_view()),
        name='djinn_forms_fileupload'
        ),
    )
