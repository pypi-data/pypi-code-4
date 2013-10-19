from django.contrib import admin

from .models import Country, Initiative, CountryInitiative, Signature


class CountryInitiativeInlineForInitiative(admin.TabularInline):
    model = CountryInitiative
    extra = 0

class CountryInitiativeInlineForCountry(admin.TabularInline):
    model = CountryInitiative
    extra = 0

class SignatureInline(admin.TabularInline):
    model = Signature
    extra = 0

class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', )
    list_display_links = ('code', 'name', )

    inlines = (CountryInitiativeInlineForCountry, )

class InitiativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'website', 'registration_date', 'deadline', 'total_signatures', 'last_checked_on', )
    actions = ('write_current_data', )

    inlines = (CountryInitiativeInlineForInitiative, )

    def write_current_data(self, request, queryset):
        for x in queryset:
            x.write_current_data()

class CountryInitiativeAdmin(admin.ModelAdmin):
    list_display = ('initiative', 'country', 'threshold', 'last_checked_on', 'current_count', 'current_percentage', )
    list_display_links = ('initiative', 'country', )
    list_filter = ('initiative', 'country', )

    fieldsets = (
        (None, {
            'fields': (
                'threshold',
            )
        }),
        ('Current data', {
            'fields': (
                ('last_checked_on', 'current_count', 'current_percentage'),
            )
        }),
    )

                

    inlines = (SignatureInline, )

class SignatureAdmin(admin.ModelAdmin):
    list_display = ('country_initiative', 'timestamp', 'count', )
    list_display_links = ('country_initiative', 'timestamp', )


admin.site.register(Country, CountryAdmin)
admin.site.register(Initiative, InitiativeAdmin)
admin.site.register(CountryInitiative, CountryInitiativeAdmin)
admin.site.register(Signature, SignatureAdmin)
