from django.contrib import admin
from .models import Person

class PersonAdmin( admin.ModelAdmin ):
	list_display = ( 'name', 'ssn', 'address', 'postcode', 'blocked' )
	list_filter = ('sex',)
	search_fields = ('name', 'ssn')
	
admin.site.register( Person, PersonAdmin )