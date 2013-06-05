from django.contrib import admin
from models import LocationType, Phone, Address, Email,  Person, Company, \
                   WebSite, Group, CustomData, IdentityData

admin.site.register(LocationType)
admin.site.register(Phone)
admin.site.register(Address)
admin.site.register(Email)
admin.site.register(WebSite)
admin.site.register(Group)
admin.site.register(CustomData)
admin.site.register(IdentityData)

admin.site.register(Person)
admin.site.register(Company)

