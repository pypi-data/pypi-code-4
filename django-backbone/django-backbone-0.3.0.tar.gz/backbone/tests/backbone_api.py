import backbone
from backbone.views import BackboneAPIView
from backbone.tests.forms import BrandForm
from backbone.tests.models import Product, Brand, ExtendedProduct


class ProductBackboneView(BackboneAPIView):
    def sku(obj):
        return '#: %s' % obj.sku

    model = Product
    display_fields = (
        'creation_date', 'name', 'brand', 'categories', 'price', 'order',
        'is_priced_under_10', 'get_first_category_id', sku, 'custom2')
    fields = ('name', 'brand', 'categories', 'price', 'order',)
    ordering = ('order', 'id')

    def custom2(self, obj):
        return 'custom2: %s' % obj.name

    def queryset(self, request):
        qs = super(ProductBackboneView, self).queryset(request)
        return qs.filter(is_hidden=False)

    def has_add_permission_for_data(self, request, cleaned_data):
        if cleaned_data['name'] == 'NOTALLOWED':
            return False
        else:
            return True

    def has_update_permission_for_data(self, request, cleaned_data):
        if cleaned_data['name'] == 'NOTALLOWED':
            return False
        else:
            return True

backbone.site.register(ProductBackboneView)


class BrandBackboneView(BackboneAPIView):
    model = Brand
    form = BrandForm
    display_fields = ['name',]
    fields = ('name',)
    paginate_by = 2

    def has_delete_permission(self, request, obj):
        return False

backbone.site.register(BrandBackboneView)


class ExtendedProductBackboneView(BackboneAPIView):
    model = ExtendedProduct
    display_fields = ('creation_date', 'name', 'brand', 'categories',
        'price', 'order', 'is_priced_under_10', 'get_first_category_id', 'description',)

backbone.site.register(ExtendedProductBackboneView)
