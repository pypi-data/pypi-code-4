import datetime

import rest_api

from models import PublicHoliday

class PublicHolidayApi(rest_api.ModelApi):
    def index(self, request):
        year = request.GET.get('year', None)
        country = request.GET.get('country', None)
        province = request.GET.get('province', None)
        
        assert year, "Year must be provided"
        assert country, "Country must be provided"
        
        start = datetime.date(int(year), 1, 1)
        finish = datetime.date(int(year)+1, 1, 1)
        
        result = self.queryset(request).filter(country=country.upper(),
            date__gte=start, date__lt=finish)
        
        if province:
            result = result.filter(Q(provinces__contains=province)|Q(provinces=None))
        
        return result

rest_api.site.register(PublicHoliday, PublicHolidayApi)