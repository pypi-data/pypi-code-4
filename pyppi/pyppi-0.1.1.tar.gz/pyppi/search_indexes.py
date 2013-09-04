from haystack import indexes
#from haystack.sites import site
from models import Package, Release


class PackageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Package.objects.all()

    def get_model(self):
        return Package

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


class ReleaseIndex(indexes.ModelSearchIndex, indexes.Indexable):
    class Meta:
        model = Release
    #text = indexes.CharField(document=True, use_template=True)
    #package_info = indexes.CharField(model_attr='package_info')
    #
    #def get_model(self):
    #    return Release
    #
    #def prepare_package_info(self, obj):
    #    return str(obj.package_info)



#site.register(Package, PackageIndex)

#site.register(Package, PackageIndex)
