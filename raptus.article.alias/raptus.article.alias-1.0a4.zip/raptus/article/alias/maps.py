from raptus.article.maps.adapters import Maps as BaseMaps, Markers as BaseMarkers
from raptus.article.alias.base import ProviderMixin

class Maps(BaseMaps, ProviderMixin):

    def getMaps(self, **kwargs):
        return self.convertAliasBrains(super(Maps, self).getMaps(**kwargs))

class Markers(BaseMarkers, ProviderMixin):

    def getMarkers(self, **kwargs):
        return self.convertAliasBrains(super(Markers, self).getMarkers(**kwargs))
