import BAPDatabase
from App.ImageFile import ImageFile

def initialize(context):
    """
        Product initialization method
        @param context: Zope server context
    """
    context.registerClass(
        BAPDatabase.BAPDatabase,
        constructors = (
            BAPDatabase.manage_add_html,
            BAPDatabase.manage_add_bap),
    )

misc_ = {
    'bap.js':ImageFile('www/js/bap.js', globals()),
    'bap_community_report.js': ImageFile('www/js/bap_community_report.js', globals()),
    'bapCompare.js':ImageFile('www/js/bap_compare.js', globals()),
    'showLoading.js':ImageFile('www/js/showLoading.js', globals()),
    'tabs-ie.css':ImageFile('www/css/tabs-ie.css', globals()),
    'full-width-style.css':ImageFile('www/css/full-width-style.css', globals()),
    'bap_style.css':ImageFile('www/css/bap_style.css', globals()),
    'ajax-loader.gif':ImageFile('www/ajax-loader.gif', globals()),
    'side-by-side.png':ImageFile('www/side-by-side.png', globals()),
    'bullet_orange.png':ImageFile('www/bullet_orange.png', globals()),
    'bullet_blue.png':ImageFile('www/bullet_blue.png', globals()),
    'bullet_red.png':ImageFile('www/bullet_red.png', globals()),
    'up.png':ImageFile('www/up.png', globals()),
    'down.png':ImageFile('www/down.png', globals()),
    'expand.png':ImageFile('www/expand.png', globals()),
    'collapse.png':ImageFile('www/collapse.png', globals()),
}
