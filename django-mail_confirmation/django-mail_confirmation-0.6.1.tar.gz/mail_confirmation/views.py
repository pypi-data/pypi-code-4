from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from .models import MailConfirmation

from .signals import confirmed as confirmed_signal


class Confirm(TemplateView):

    def dispatch(self, request, confirmationid, *args, **kwargs):
        confirmation = get_object_or_404(MailConfirmation,
                                         confirmationid=confirmationid, 
                                         confirmed=False)
        confirmation.confirmed = True
        confirmation.save()
        self.template_name = confirmation.confirm_success_template or confirmation.toconfirm_object._meta.app_label+'/mail_confirmation_succeeded.html'
        confirmed_signal.send(sender=MailConfirmation, 
                              toconfirm_type=confirmation.toconfirm_object.__class__, 
                              object_id=confirmation.toconfirm_object.id)
        if confirmation.confirm_success_url:
            return HttpResponseRedirect(confirmation.confirm_success_url)

        return super(Confirm, self).dispatch(request, *args, **kwargs)
