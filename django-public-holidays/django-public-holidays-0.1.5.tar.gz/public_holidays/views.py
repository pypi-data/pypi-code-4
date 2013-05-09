# Some useful views related to public holidays.

import datetime
import simplejson as json

from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse

from django_countries.fields import Country

from models import PublicHoliday

def holidays(request, country, year, other_year=None, province=None):
    start = datetime.date(int(year), 1, 1)
    if other_year:
        finish = datetime.date(int(other_year), 12, 31)
    else:
        finish = datetime.date(int(year), 12, 31)
        
    country = country.upper()
    
    holidays = PublicHoliday.objects.for_country(country, province).between(start, finish)
        
    if 'HTTP_ACCEPT' in request.META:
        if 'application/json' in request.META['HTTP_ACCEPT']:
            format = 'json'
        else:
            format = 'html'
    else:
        format = request.GET.get('format', 'html')

    if format == "json":
        return HttpResponse(json.dumps(holidays.as_json()))
    
    country = Country(country)
    provinces = dict(country.provinces_select.choices)

    context = {
        'holidays': holidays.as_json(),
        'country': country,
        'start': start,
        'finish': finish,
        'province': provinces.get(province, None),
    }
    
    return render(request, 'public_holidays/year.%s' % format, context)