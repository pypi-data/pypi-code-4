import os
from csat.django.apps.base import bundles


three_js = bundles.make_js_bundle('three', [
    'js/three.js',
    'js/stats.js',
], filters=bundles.jsfilters)

master = bundles.make_js_bundle('visualization', [
    bundles.coffee('viewer.old'),
    bundles.coffee('visualization'),
], filters=['coffeescript'] + bundles.jsfilters)

fonts = bundles.make_js_bundle('fonts', [
    'js/helvetiker.typeface.js',
], filters=bundles.jsfilters)

master = bundles.make_js_bundle('viewer', [
    bundles.coffee('lib'),
    bundles.coffee('iterator'),
    bundles.coffee('bezier-editor'),
    bundles.coffee('exporters/gexf'),
    bundles.coffee('views'),
    bundles.coffee('rendering'),
    bundles.coffee('algo-config'),
    bundles.coffee('layout'),
    bundles.coffee('graph'),
    bundles.coffee('strategies'),
    bundles.coffee('viewer'),
], filters=['coffeescript'] + bundles.jsfilters)


# Web worker layouts
basedir = os.path.join(
    os.path.dirname(__file__),
    'assets', 'coffeescripts', 'workers'
)

coffeebase = bundles.make_js_bundle(
    '_worker_base_coffee',
    [
        bundles.coffee('lib'),
        bundles.coffee('iterator'),
        bundles.coffee('workers/base'),
    ],
    register=False,
    filters=['coffeescript'],
)

jsbase = bundles.make_js_bundle('_worker_base_js', [
    'js/vector3.js',
    coffeebase,
], register=False)

for path in os.listdir(basedir):
    if path == 'base.coffee':
        continue

    asset = os.path.join('coffeescripts', 'workers', path)
    name = path.rsplit('.', 1)[0]

    impl = bundles.make_js_bundle(
        '_worker_{}_implementation'.format(name),
        [asset],
        filters=['coffeescript'],
        register=False
    )
    bundles.make_js_bundle(
        'worker_{}'.format(name),
        [jsbase, impl],
        filters=bundles.jsfilters,
        output='scripts/workers/{}{}.js'.format(name, bundles.postfix),
    )

#benchmarks = bundles.make_js_bundle('benchmarks_base', [
#    bundles.coffee('views'),
#    bundles.coffee('rendering'),
#    bundles.coffee('layout'),
#    bundles.coffee('graph'),
#    bundles.coffee('benchmarks'),
#], filters=['coffeescript'])

#bundles.make_js_bundle('benchmarks', [
#    seedrandom,
#    benchmarks,
#])
