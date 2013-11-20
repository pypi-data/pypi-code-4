# -*- coding: utf-8 -*-


class OnlyChangeAdminMixin(object):
    """Use this mixin in your ModelAdmin class to disable add/delete permissions."""
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class NoAddAdminMixin(object):
    """Use this mixin in your ModelAdmin class to disable add permissions."""
    def has_add_permission(self, request):
        return False


class NoDeleteAdminMixin(object):
    """Use this mixin in your ModelAdmin class to disable delete permissions."""
    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(NoDeleteAdminMixin, self).get_actions(request)
        del actions['delete_selected']
        return actions


class HiddenAdminMixin(object):
    """Use this mixin in your ModelAdmin class to hide it from admin models index."""
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        Based on: http://stackoverflow.com/a/4871511/334446
        """
        return {}
