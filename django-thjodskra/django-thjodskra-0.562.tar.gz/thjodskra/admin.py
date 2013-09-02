from django.contrib import admin
from .models import Person, Organisation

class PersonAdmin( admin.ModelAdmin ):
	list_display = ( 'name', 'ssn', 'address', 'postcode', 'blocked' )
	list_filter = ('sex', 'postcode')
	search_fields = ('name', 'ssn')	
admin.site.register( Person, PersonAdmin )

class OrganisationAdmin( admin.ModelAdmin ):
	list_display = ( 'name', 'ssn', 'address', 'postcode', 'activity', 'recipient', 'is_deregistered', 'blocked' )
	list_filter = ('postcode',)
	search_fields = ('name', 'ssn')	
admin.site.register( Organisation, OrganisationAdmin )