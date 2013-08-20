from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required, permission_required
from cron_monitor import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^begin$', views.begin_run, name='begin'),
    url(r'^finish$', views.finished_run, name='finish'),
    url(r'^delete_rec$', views.delete_record, name='delete'),
    url(r'^delete_job$', views.delete_job, name='delete_job'),
    url(r'^htmllog/(?P<rec_id>\d+)$', views.see_html_log, name='html_log'),
    url(r'^plainlog/(?P<log_id>\d+)$', views.see_plain_log, name='plain_log'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^settings/add$',
        login_required
        (permission_required('cron_monitor.add_emailsettings',
                             raise_exception=True)
        (views.SettingsCreate.as_view())),
        name='settings_add'),
    url(r'^settings/(?P<pk>\d+)$',
        login_required
        (permission_required('cron_monitor.change_emailsettings',
                             raise_exception=True)
        (views.SettingsUpdate.as_view())),
        name='settings_update'),
    url(r'^emails/$',
        views.GlobalEmailListView.as_view(), name='global'),
    url(r'^emails/add$',
        login_required
        (permission_required('cron_monitor.add_globalemailaddress',
                             raise_exception=True)
        (views.GlobalEmailCreate.as_view())),
        name='global_add'),
    url(r'^emails/delete$',
        login_required
        (permission_required('cron_monitor.delete_globalemailaddress',
                             raise_exception=True)
        (views.global_email_delete)),
        name='global_delete'),
)
