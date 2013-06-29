from django.utils.translation import ugettext_lazy as _

from player.block import Block, register_block


class NavBlock(Block):
    """ Navigation block """
    name = 'navigationblock'
    label = _('Navigation block')

    def render(self, request, context):
        return self.render_block(request, template_name='website/nav_block.html',
                          block_title="Nav block",
                          context=context)

register_block(NavBlock)
