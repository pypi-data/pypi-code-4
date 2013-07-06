from csat.django.apps.base.bundles import make_css_bundle, make_js_bundle
from csat.django.apps.base.bundles import coffee, jsfilters

from csat.django.apps.bootstrap import assets as bootstrap


custom_styles = make_css_bundle('custom', [
    'sass/*/screen.sass',
], filters=['compass'], depends=['sass/*/*.sass'], register=False)

screen_css = make_css_bundle('screen', [
    'css/pygments.css',
    custom_styles,
], register=False)

all_css = make_css_bundle('master', [
    bootstrap.css,
    custom_styles,
], filters=['cssmin', ])


jquery = make_js_bundle('jquery', [
    'js/jquery-1.9.1.js',
], register=False)

jquery_ui = make_js_bundle('jquery-ui', [
    'js/jquery-ui-1.10.2.custom.js',
], register=False)

plugins = make_js_bundle('plugins', [
    coffee('jquery.*'),
], filters=['coffeescript'], register=False)

external_libraries = make_js_bundle('base_libs', [
    jquery,
    jquery_ui,
    bootstrap.js,
    plugins,
], filters=[])

all_js = make_js_bundle('master', [
    'coffeescripts/master.coffee',
], filters=['coffeescript'] + jsfilters)
