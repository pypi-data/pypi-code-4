from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('player.block.views',
    url(r'^$', 'block_list', name='block_list'),
    url(r'^add/$', 'block_add', name='block_add'),
    url(r'^(?P<block_id>\d+)/$', 'block_detail', name='block_detail'),
    url(r'^(?P<block_id>\d+)/edit/$', 'block_edit', name='block_edit'),
    url(r'ajax/order/', 'blocks_reorder', name='blocks_reorder'),
    url(r'ajax/config/(?P<block_id>\d+)$', 'generate_blocks_configuration',
        name='generate_blocks_configuration'),
    url(r'ajax/config_by_path/(?P<block_path>[\w.]+)$', 'generate_blocks_configuration_by_path',
        name='generate_blocks_configuration_by_path'),
    url(r'ajax/add/$', 'ajax_block_add', name='ajax_block_add'),
    url(r'ajax/add/config/$', 'get_block_config', name='get_block_config'),
)
