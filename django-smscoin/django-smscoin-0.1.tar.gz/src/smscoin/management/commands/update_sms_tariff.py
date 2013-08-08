### -*- coding: utf-8 -*- ####################################################

import urllib2
from datetime import datetime
from lxml import etree

from django.core.management.base import BaseCommand

from smscoin.settings import SMSCOIN_TARIFF_PATH
from smscoin.models import Provider

DEFAULT_PARSER = etree.XMLParser(huge_tree=True, encoding='utf-8')

class Command(BaseCommand):
    """Updates SMSCOIN's tariffs."""
    help = """Updates SMSCOIN's tariffs."""

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        
        response = urllib2.urlopen(SMSCOIN_TARIFF_PATH)
        
        now = datetime.now()
        
        def fill_provider(country_code, el):
            data = {
                'number': el.get('number'),
                'prefix': el.get('prefix'),
                'rewrite': el.get('rewrite'),
                'price': el.get('price'),
                'currency': el.get('currency'),
                'usd': el.get('usd'),
                'profit': el.get('profit'),
                'vat': el.get('vat') == '1',
                'notice': el.get('special'),
                'name': el.get('name'),
                'code': el.get('code'),
            }
            
            obj, created = Provider.objects.get_or_create(country=country_code, code=el.get('code'), defaults=data)
            
            if not created:
                for field_name, field_value in data.items():
                    setattr(obj, field_name, field_value)
            
            obj.modified = now
            obj.save()
            
            return obj
            
        
        for country_element in etree.parse(response, parser=DEFAULT_PARSER).xpath('/feed/slab'):
            
            country = country_element.get('country')
            
            if verbosity >= 2:
                print(country_element.get('country_name').encode('utf-8'))
            
            if country_element.get('number'):
                fill_provider(country, country_element)
            else:
                
                for provider_element in country_element:
                    if verbosity >= 2:
                        print("-- %s" % provider_element.get('name').encode('utf-8'))
                    
                    fill_provider(country, provider_element)
        
        Provider.objects.exclude(modified=now).delete()
        