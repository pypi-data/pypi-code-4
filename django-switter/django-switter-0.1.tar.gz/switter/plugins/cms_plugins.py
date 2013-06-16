from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from switter.plugins.models import SwitterTweets


class SwitterTweetsPlugin(CMSPluginBase):
    model = SwitterTweets
    name = "Tweets"
    admin_preview = False

    def render(self, context, instance, placeholder):
        context.update({
            'placeholder': placeholder,
            'object': instance,
            })
        return context


plugin_pool.register_plugin(SwitterTweetsPlugin)
