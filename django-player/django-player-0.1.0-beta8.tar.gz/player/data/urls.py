from django.conf import settings
from django.conf.urls.defaults import patterns, url


slug_re = settings.SLUG_RE

urlpatterns = patterns('player.data.views',
    (r'^collectiongroups/$', 'collectiongroup_list'),
    url(r'^collectiongroups/add/$', 'collectiongroup_add', name='collectiongroup_add'),
    url(r'^collectiongroups/(?P<slug>%s)/$' % slug_re, 'collectiongroup_view', name='collectiongroup_view'),
    url(r'^collectiongroups/(?P<slug>%s)/edit/$', 'collectiongroup_edit', name='collectiongroup_edit'),
    url(r'^collectiongroups/(?P<slug>%s)/collection/(?P<collection_slug>%s)/$' % (slug_re, slug_re), 'collection_view', name='collection_view'),
    url(r'^collectiongroups/(?P<slug>%s)/collection/(?P<collection_slug>%s)/edit/$' % (slug_re, slug_re), 'collection_edit', name='collection_edit'),
    url(r'^collectiongroups/(?P<slug>%s)/collection/(?P<collection_slug>%s)/scrap_association/$' % (slug_re, slug_re),
        'scrap_association', name='scrap_association'),
    (r'^collectiongroups/(?P<slug>%s)/collection/(?P<collection_slug>%s)/publish/$' % (slug_re, slug_re), 'collection_publish'),
    (r'^collectiongroups/(?P<slug>%s)/collection/(?P<collection_slug>%s)/unpublish/$' % (slug_re, slug_re), 'collection_unpublish'),
    url(r'^collectiongroups/(?P<slug>%s)/collection/(?P<collection_slug>%s)/crawl/$' % (slug_re, slug_re), 'collection_crawl', name='collection_crawl'),
    (r'^collectiongroups/(?P<slug>%s)/collection/(?P<collection_slug>%s)/edit-fields/$' % (slug_re, slug_re), 'collection_edit_fields'),
    (r'^collectiongroups/(?P<slug>%s)/collection/(?P<collection_slug>%s)/fields-in-json/$' % (slug_re, slug_re), 'collection_fields_in_json'),
    url(r'^collectiongroups/(?P<slug>%s)/collection/(?P<collection_slug>%s)/steps/toggle-crawling-checked$' % (slug_re, slug_re),
        'collection_toggle_crawling_checked', name='collection_toggle_crawling_checked'),
    (r'^collectiongroups/(?P<slug>%s)/item/(?P<item_id>\w+)/$' % settings.SLUG_RE, 'item_view'),
    (r'^collectiongroups/(?P<slug>%s)/item/(?P<item_id>\w+)/validate/$' % settings.SLUG_RE, 'item_validate'),
    (r'^collections/$', 'collection_list'),
    url(r'^collections/add/$', 'collection_add', name='collection_add'),
)
