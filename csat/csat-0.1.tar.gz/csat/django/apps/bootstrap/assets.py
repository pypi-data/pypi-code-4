from csat.django.apps.base.bundles import make_css_bundle, make_js_bundle


css = make_css_bundle('bootstrap', [
    'sass/bootstrap-include.sass',
], filters=['compass'])


js = make_js_bundle('bootstrap', [
    'js/bootstrap-tooltip.js',
    'js/bootstrap-*.js',
    'js/bootstrap-popover.js',
])
