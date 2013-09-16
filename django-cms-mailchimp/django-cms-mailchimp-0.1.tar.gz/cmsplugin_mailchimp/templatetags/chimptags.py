from classytags.arguments import Argument, StringArgument
from classytags.core import Options
from classytags.helpers import InclusionTag
from django import template

from ..forms import SubscribeForm

register = template.Library()

class Subscribe(InclusionTag):
    name = 'mailchimp_subscribe_form'
    template = 'cmsplugin_mailchimp/subscribe.html'
    options = Options(
        Argument('list_id'),
        StringArgument('template', default='cmsplugin_mailchimp/subscribe.html', required=False),
    )

    def get_context(self, context, list_id, template):
        subscribeForm = SubscribeForm(initial={'list_id': list_id})
        return context.update({
            'csrf_token': context['csrf_token'],
            'form': subscribeForm,
            'template': template,
            })

register.tag(Subscribe)