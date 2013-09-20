from django.conf.urls.defaults import *

from nano.comments.models import *

comment_dict = {}


urlpatterns = patterns('nano.comments.views',
    (r'^$',         'list_comments', comment_dict, 'comments-list-comments'),
    (r'^post$',     'post_comment', {}, 'comments-post-comment'),
)

urlpatterns += patterns('',
    url(r'^cr/(\d+)/(.+)/$', 'django.views.defaults.shortcut', name='comments-url-redirect'),
)

