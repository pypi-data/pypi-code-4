from django.conf.urls.defaults import *

urlpatterns = patterns('nano.privmsg.views',
    url(r'^add$',          'add_pm', name='add_pm'),
    url(r'^(?P<msgid>[1-9][0-9]*)/archive$', 'move_to_archive', name='archive_pm'),
    url(r'^(?P<msgid>[1-9][0-9]*)/delete$', 'delete', name='delete_pm'),
    #url(r'^(?:(?P<action>(archive|sent))/?)?$', 'show_pms', name='show_pms'),
    url(r'^archive/$', 'show_pm_archived', name='show_archived_pms'),
    url(r'^sent/$', 'show_pm_sent', name='show_sent_pms'),
    url(r'^$', 'show_pm_received', name='show_pms'),
    #url(r'^$', 'show_pms', {u'action': u'received'}, name='show_pms'),
)

