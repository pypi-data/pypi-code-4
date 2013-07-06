from django.conf.urls import patterns, url


urlpatterns = patterns(
    'csat.acquisition.views',

    url(
        r'^$',
        'session_index',
        name='session-index'
    ),
    url(
        r'^new/$',
        'session_create',
        name='session-create'
    ),
    url(
        r'^(?P<pk>\d+)/$',
        'session_view',
        name='session'
    ),
    url(
        r'^(?P<pk>\d+)/edit/$',
        'session_edit',
        name='session-edit'
    ),
    url(
        r'^(?P<pk>\d+)/reset/$',
        'session_reset',
        name='session-reset'
    ),
    url(
        r'^(?P<pk>\d+)/run/$',
        'session_run',
        name='session-run'
    ),
    url(
        r'^(?P<pk>\d+)/thumbnail.png$',
        'session_thumbnail',
        name='session-thumbnail'
    ),
    url(
        r'^(?P<pk>\d+)/delete/$',
        'session_delete',
        name='session-delete'
    ),

    url(
        r'^results/(?P<result_id>[^/]+)/$',
        'collector_upload_results',
        name='collector-upload-results'
    ),

    url(
        r'^(?P<session_pk>\d+)/add/(?P<collector>[^/]+)/$',
        'collector_create',
        name='collector-create'
    ),
    url(
        r'^(?P<session_pk>\d+)/edit/(?P<collector_pk>\d+)/$',
        'collector_edit',
        name='collector-edit'
    ),
    url(
        r'^(?P<session_pk>\d+)/delete/(?P<collector_pk>\d+)/$',
        'collector_remove',
        name='collector-remove'
    ),

    url(
        (r'^(?P<session_pk>\d+)/(?P<collector_pk>\d+)/log.'
         '(?P<format>txt|html)?$'),
        'collector_view_log',
        name='collector-view-log'
    ),
    url(
        (r'^(?P<session_pk>\d+)/(?P<collector_pk>\d+)/graph.'
         '(?P<format>graphml|html)?$'),
        'collector_view_results',
        name='collector-view-results'
    ),
    url(
        r'^(?P<session_pk>\d+)/graph.(?P<format>html|graphml)?$',
        'session_view_results',
        name='session-view-results'
    ),
)
