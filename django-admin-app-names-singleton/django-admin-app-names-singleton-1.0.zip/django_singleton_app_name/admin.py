from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.utils import six
from django.template.response import TemplateResponse
from django.contrib import admin
from models import SingletonBaseModel

class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_dict = {}
        user = request.user
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = user.has_module_perms(app_label)

            if has_module_perms:
                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    info = (app_label, model._meta.module_name)
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'perms': perms,
                    }
                    try:
                        model_dict['single_instance'] = model.single_instance()
                        if model_dict['single_instance']:
                            model_objects = model.objects.all()
                            if len(model_objects):
                                model_dict['instance_id'] = model_objects[0].id
                            else:
                                model_dict['instance_id'] = -1
                    except AttributeError:
                        model_dict['single_instance'] = False
                    if perms.get('change', False):
                        try:
                            model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if perms.get('add', False):
                        try:
                            model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_name = _(app_label)
                        app_dict[app_label] = {
                            'name': app_name,
                            'app_url': reverse('admin:app_list', kwargs={'app_label': app_label}, current_app=self.name),
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the apps alphabetically.
        app_list = list(six.itervalues(app_dict))
        app_list.sort(key=lambda x: x['name'])

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        context = {
            'title': _('Site administration'),
            'app_list': app_list,
        }
        context.update(extra_context or {})
        return TemplateResponse(request, self.index_template or
                                'admin/index.html', context,
                                current_app=self.name)


class SingletonModelAdmin(admin.ModelAdmin):
    model = SingletonBaseModel

    def has_add_permission(self, request):
        if self.model.objects.count():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(SingletonModelAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions


new_admin_site = CustomAdminSite()
new_admin_site._registry = admin.site._registry
admin.site = new_admin_site
