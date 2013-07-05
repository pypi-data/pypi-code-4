from csat.django.apps.base import bundles


master = bundles.make_js_bundle('acquisition', [
    bundles.coffee('acquisition'),
], filters=['coffeescript'])
