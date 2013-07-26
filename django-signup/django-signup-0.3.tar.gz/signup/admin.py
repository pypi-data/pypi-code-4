from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import get_current_site

from .models import Validation

class ValidationAdmin(admin.ModelAdmin):
	def send_activation_emails(self, request, queryset):

		site = get_current_site(request)
		for validation in queryset:
			validation.send_activation_email(site)

		msg = u'Sent %i email(s)' % len(queryset)
		self.message_user(request, msg)
	send_activation_emails.short_description = _(u'Resend activation email')

	list_display = ('user', 'created')
	actions = ('send_activation_emails',)
	readonly_fields = ('user', 'key')

admin.site.register(Validation, ValidationAdmin)
