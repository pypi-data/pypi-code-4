from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.forms.models import BaseInlineFormSet
from django.conf import settings

class LitBaseAdmin(admin.ModelAdmin):
    exclude = ('lit_default_unicode',)
    def queryset(self, request):
        qs = self.model.litobjects.all()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

class LitAdmin(admin.ModelAdmin):
    """
    Base Admin for Lit Models
    """
    fieldsets = ((_(u"Translation"),{
                    'fields':(('language',),),
                    'classes': ('collapse',)}),)
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "language":
            kwargs['initial'] = settings.LANGUAGE_CODE
        return super(LitAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    

class CycleTranslation(object):
    """
    It returns a list of tuples with all combinations made with languages. 
    All LitModel classes inherit an admin's form with prepopulated language.
    """
    positions = {}
    
    def __init__(self):
        cont = 0
        for lang in settings.LANGUAGES:
            self.positions['%s' % cont] = lang
            cont = cont + 1
        

class LitInlineFormset(BaseInlineFormSet):
    """
    This is the formset inherited in LitInlineModel classes
    """
    def __init__(self, data=None, files=None, instance=None,
                 save_as_new=False, prefix=None, queryset=None):
        
        super(LitInlineFormset, self).__init__(data, files, instance,
                 save_as_new, prefix, queryset) 
        cycle_translation= CycleTranslation()
        cont = 0
        if not data and cycle_translation.positions:
            for form in self.forms:
                lang = cycle_translation.positions['%s' % cont]
                
                form.fields['language'].initial = lang[0]
                cont  = cont + 1
                form.empty_permitted = True
                     
            
class LitStackedInlineAdmin(admin.StackedInline):
    """
    It defines a StackedInlineAdmin for all LitModelInline
    """
    def __init__(self, parent_model, admin_site):
        super(LitStackedInlineAdmin,self).__init__(parent_model, admin_site)
        max_num = len(settings.LANGUAGES)
        self.max_num = max_num
        self.extra = max_num

        
    formset = LitInlineFormset
    template = "admin/lit_tabs_stacked.html"
    class Media: 
        css = {"all" : (settings.STATIC_URL +"lit/css/lit-stacked-tabs.css",)}
        js = (settings.STATIC_URL +'lit/js/jquery-1.9.0.js',
              settings.STATIC_URL +'lit/js/litinline.js',
              settings.STATIC_URL +'lit/js/littabsinline.js',
              )
        
class LitTabularInlineAdmin(admin.TabularInline):
    """
    It defines a TabularInlineAdmin for all LitModelInline
    """
    def __init__(self, parent_model, admin_site):
        super(LitTabularInlineAdmin,self).__init__(parent_model, admin_site)
        max_num = len(settings.LANGUAGES)
        self.max_num = max_num
        self.extra = max_num

    formset = LitInlineFormset
    class Media: 
        js = (settings.STATIC_URL +'lit/js/jquery-1.9.0.js',
              settings.STATIC_URL +'lit/js/littabsinline.js',)
    