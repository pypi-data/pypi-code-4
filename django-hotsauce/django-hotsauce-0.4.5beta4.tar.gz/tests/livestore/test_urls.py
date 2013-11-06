import os.path
from notmm.utils.urlmap import RegexURLMap

from django.contrib import admin
admin.autodiscover()

urlpatterns = RegexURLMap()

# home.py views
urlpatterns.include('satchmo_store.shop.urls', prefix='^shop/')

# debug views
#urlpatterns.add_routes('',    
#    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
#        {'document_root': os.path.join(os.path.dirname(__file__), 'media/')})
#    )

urlpatterns.include('product.urls.base')
urlpatterns.include('product.urls.category')

# django admin views
urlpatterns.include(admin.site.urls, prefix='^admin/')

#urlpatterns.commit()

__all__ = ['urlpatterns']

