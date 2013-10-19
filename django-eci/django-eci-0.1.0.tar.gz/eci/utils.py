import requests
import datetime
from decimal import Decimal

from django.utils import timezone
from django.db import models


def fetch_current_data(url):
    r = requests.get(url)
    return r.json()

def write_current_data(initiative, data=None, now=None):
    from .models import Country, CountryInitiative, Signature

    if data is None:
        data = fetch_current_data(initiative.data_url)
    if now is None:
        now = timezone.now()

    # make sure there is country created
    for x in data['countries']:
        Country.create_if_needed(x['code'], x['name'])

    # update total signatures
    initiative.total_signatures = int(data['total'])
    initiative.last_checked_on = now
    initiative.save()

    # create new signatures
    for x in data['countries']:
        country = Country.objects.get(code=x['code'])
        try:
            country_initiative = CountryInitiative.objects.get(
                country=country, initiative=initiative)
            last_count = country_initiative.current_count
        except CountryInitiative.DoesNotExist:
            country_initiative = CountryInitiative(country=country, initiative=initiative)
            last_count = 0

        country_initiative.threshold = int(x['threshold'])
        country_initiative.current_count = int(x['count'])
        country_initiative.current_percentage = Decimal(x['percentage'])
        country_initiative.last_checked_on = now

        country_initiative.save()

        Signature.objects.create(country_initiative=country_initiative,
                                 timestamp=now,
                                 count=int(x['count']) - last_count,
                                 percentage=Decimal(x['percentage']))
