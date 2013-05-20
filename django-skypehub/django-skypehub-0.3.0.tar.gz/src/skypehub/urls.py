from django.conf.urls.defaults import url, patterns


urlpatterns = patterns(
    'skypehub.views',
    url(r'^list_chats$', 'list_chats', name='skype_list_chats'),
    url(r'^post_message', 'post_message', name='skype_post_message'),
)
