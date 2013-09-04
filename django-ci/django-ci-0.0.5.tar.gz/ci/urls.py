import traceback
try:
    from django.conf.urls import patterns, url, include
    from viewsets import ViewSet
    import views

    defaultpatterns = patterns(r'^ci/', include("ci.urls"))

    urlpatterns = ViewSet.all_urls()

    urlpatterns += patterns('',
    )
except:
    traceback.print_exc()
