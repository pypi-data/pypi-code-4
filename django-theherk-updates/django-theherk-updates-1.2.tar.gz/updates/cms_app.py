from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class UpdatesApphook(CMSApp):
    name = _("Updates Apphook")
    urls = ["updates.urls"]
    app_name = "updates"

apphook_pool.register(UpdatesApphook)
