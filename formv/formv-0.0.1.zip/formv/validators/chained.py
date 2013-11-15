#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import formv
from datetime import date
from formv.validators.base import VBase
from formv.exception import Invalid
from formv.utils.geodist import GeoDistance
from formv.utils import empty, match, extract_text as _
from formv.utils.compat import iteritems

__all__ = ('VAllFields','VAnyField','VCreditCard','VCurrency','VGeoDistance',
           'VLanguage','VPair','VPhoneFormat','VCountryPostcode',
           'VCountryStatePostcode', 'VPostcodeFormat', 'VState',)

class VAnyField(VBase):
    """ at least one field must have a value """
    def __init__(self, fields, msg, **kw):
        VBase.__init__(self, **kw)
        self.fields = fields
        self.msg = msg

    def _validate(self, form):
        for f in self.fields:
            if form.get(f) and form[f]:
                return
        raise Invalid(self.msg, form)


class VAllFields(VBase):
    """ all fields must have a value """
    def __init__(self, fields, msg, **kw):
        VBase.__init__(self, **kw)
        self.fields = fields
        self.msg = msg

    def _validate(self, form):
        for f in self.fields:
            if not form.get(f) or empty(form[f]):
                raise Invalid(self.msg, form)


class VPair(VBase):
    """ if available_field has a value, required_field must have one too """
    def __init__(self, required_field, required_label, 
                 available_field, must_be_equal=False, **kw):
        VBase.__init__(self, **kw)
        self.required_field = required_field
        self.available_field = available_field
        self.required_label = required_label
        self.must_be_equal = must_be_equal

    def _validate(self, form):
        self.messages.update({'invalid': _('You must provide a value for "%(required)s"'),
                              'not_equal': _('Fields don\'t match')})        
        a = form.get(self.available_field)
        r = form.get(self.required_field)
        if self.must_be_equal and a != r:
            raise Invalid(self.message('not_equal'), form)        
        if empty(r) and a:
            raise Invalid(self.message('invalid', required=self.required_label), form)
        return r


class VCountryPostcode(VBase):
    """ validates country -> postcode relationship """
    def __init__(self, country_field, postcode_field, **kw):
        VBase.__init__(self, **kw)
        self.country_field = country_field
        self.postcode_field = postcode_field

    def _validate(self, form):
        self.messages.update({'invalid': _('Invalid postal code for %(country)s')})
        country = form.get(self.country_field)
        if country:        
            country = formv.config.countries.get(country)
        postcode = form.get(self.postcode_field)
        if country and postcode:
            coords = country.postcodes.get(postcode.upper())
            if coords:
                return (float(coords[0]), float(coords[1]))
            raise Invalid(self.message('invalid', country=country.name), postcode)


class VCountryStatePostcode(VBase):
    """ validates country -> state -> postcode relationship """
    def __init__(self, country_field, state_field, postcode_field, **kw):
        VBase.__init__(self, **kw)
        self.country_field = country_field
        self.state_field = state_field
        self.postcode_field = postcode_field

    def _validate(self, form):
        self.messages.update({'invalid': _('Invalid postal code for %(state)s, %(country)s')})
        country = form.get(self.country_field)
        if country:        
            country = formv.config.countries.get(country)
        state = form.get(self.state_field)
        if state:
            state = country.states.get(state)
        postcode = form.get(self.postcode_field)
        if country and state and postcode:
            coords = state.postcodes.get(postcode.upper())
            if coords:
                return (float(coords[0]), float(coords[1]))
            raise Invalid(self.message('invalid', country=country.name, state=state.name), postcode)


class VPostcodeFormat(VBase):
    def __init__(self, country_field, postcode_field, **kw):
        VBase.__init__(self, **kw)
        self.country_field = country_field
        self.postcode_field = postcode_field

    def _validate(self, form):
        self.messages.update({'invalid': _('Invalid postal code format for %(country)s')})        
        country = form.get(self.country_field)
        if country:        
            country = formv.config.countries.get(country)
        postcode = form.get(self.postcode_field)         
        if country and postcode:
            try:
                return match(country.formats.postcode, postcode)
            except ValueError:
                raise Invalid(self.message('invalid', country=country.name), postcode)


class VState(VBase):
    def __init__(self, country_field, state_field, mode='by-code', **kw):
        VBase.__init__(self, **kw)
        self.country_field = country_field
        self.state_field = state_field
        assert mode in ('by-code','by-name')
        self.mode = mode        
            
    def _validate(self, value):     
        self.messages.update({'invalid': _('Invalid state/province for %(country)s')})        
        if self.mode == 'by-code':
            return self._by_code(value)
        if self.mode == 'by-name':
            return self._by_name(value)
                    
    def _by_code(self, value):
        country = value.get(self.country_field)
        if country:        
            country = formv.config.countries.get(country)
        state = value.get(self.state_field)
        if country and state:
            if country.states.get(state.upper()):
                return state.upper()
            raise Invalid(self.message('invalid', country=country.name), state)
                        
    def _by_name(self, value):
        country = value.get(self.country_field)
        if country:        
            country = formv.config.countries.get(country)
        state = value.get(self.state_field)
        if country and state:
            for k, state_data in iteritems(country.states):
                if state.upper() in [n.upper() for n in state_data.names]:
                    return k
            raise Invalid(self.message('invalid', country=country.name), state)


class VCurrency(VBase):
    def __init__(self, country_field, currency_field, mode='by-code', **kw):
        VBase.__init__(self, **kw)
        self.country_field = country_field
        self.currency_field = currency_field
        assert mode in ('by-code','by-name')
        self.mode = mode        

    def _validate(self, value):      
        self.messages.update({'invalid': _('Invalid currency for %(country)s')})
        if self.mode == 'by-code':
            return self._by_code(value)
        if self.mode == 'by-name':
            return self._by_name(value)
    
    def _by_code(self, value):
        country = value.get(self.country_field)
        if country:        
            country = formv.config.countries.get(country)
        currency = value.get(self.currency_field)
        if country and currency:
            if currency.upper() in country.currencies:
                return currency.upper()
            raise Invalid(self.message('invalid', country=country.name), currency)
    
    def _by_name(self, value):
        country = value.get(self.country_field)
        currencies = {}
        if country:        
            country = formv.config.countries.get(country)
            if country: 
                for c in country.currencies:
                    currencies[c] = formv.config.currencies[c]
        currency = value.get(self.currency_field)
        if country and currencies and currency:            
            for k, names in iteritems(currencies):
                if currency.upper() in [n.upper() for n in names]:
                    return k
            raise Invalid(self.message('invalid', country=country.name), currency)


class VLanguage(VBase):
    def __init__(self, country_field, language_field, mode='by-code', **kw):
        VBase.__init__(self, **kw)
        self.country_field = country_field
        self.language_field = language_field
        assert mode in ('by-code','by-name')
        self.mode = mode        

    def _validate(self, value):   
        self.messages.update({'invalid': _('Invalid language for %(country)s')})    
        if self.mode == 'by-code':
            return self._by_code(value)
        if self.mode == 'by-name':
            return self._by_name(value)
    
    def _by_code(self, value):
        country = value.get(self.country_field)
        if country:        
            country = formv.config.countries.get(country)
        language = value.get(self.language_field)
        if country and language:  
            if country.languages.get(language.upper()):          
                return language.upper()
            raise Invalid(self.message('invalid', country=country.name), language)

    def _by_name(self, value):
        country = value.get(self.country_field)
        languages = {}
        if country:        
            country = formv.config.countries.get(country)
            if country: 
                for c in country.languages:
                    languages[c] = formv.config.languages[c]
        language = value.get(self.language_field)
        if country and languages and language:            
            for k, names in iteritems(languages):
                if language.upper() in [n.upper() for n in names]:
                    return k
            raise Invalid(self.message('invalid', country=country.name), language)


class VGeoDistance(VBase):
    def __init__(self, origin_field, destination_field, **kw):
        VBase.__init__(self, **kw)
        self.origin_field = origin_field
        self.destination_field = destination_field        
    
    def _validate(self, value):
        origin = value.get(self.origin_field)
        destination = value.get(self.destination_field)
        if origin and destination: 
            return GeoDistance(origin, destination).haversine()


class VPhoneFormat(VBase):
    def __init__(self, country_field, phone_field, **kw):
        VBase.__init__(self, **kw)
        self.country_field = country_field
        self.phone_field = phone_field

    def _validate(self, value):
        self.messages.update({'invalid': _('Invalid phone number format for %(country)s')})        
        country = value.get(self.country_field)
        if country:        
            country = formv.config.countries.get(country)
        phone = value.get(self.phone_field)         
        if country and phone:
            try:
                return match(country.formats.phone, phone)
            except ValueError:
                raise Invalid(self.message('invalid', country=country.name), phone)


class VCreditCard(VBase):
    def __init__(self, card_type_field, 
                       card_number_field, 
                       card_expiration_field, 
                       card_security_code_field, **kw):
        VBase.__init__(self, **kw)
        self.t = card_type_field
        self.n = card_number_field
        self.e = card_expiration_field
        self.c = card_security_code_field
        self.card_info = {'visa': [('4', 16), ('4', 13)],
                          'mastercard': [('51', 16), ('52', 16),  ('53', 16),
                                         ('54', 16), ('55', 16)],
                          'discover': [('6011', 16)],
                          'amex': [('34', 15), ('37', 15)],
                          'dinersclub': [('300', 14), ('301', 14), ('302', 14), 
                                         ('303', 14), ('304', 14), ('305', 14),
                                         ('36', 14), ('38', 14)],
                          'jcb': [('3', 16), ('2131', 15), ('1800', 15)]}
        self.code_info = {'visa': 3, 'mastercard': 3, 'discover': 3, 
                          'amex': 4, 'jcb': 3}
     
    def _validate(self, form):
        self.messages.update({'invalid': _('Invalid credit card details'),
                              'invalid_t': _('Invalid credit card type'),
                              'invalid_n': _('Invalid credit card number'),
                              'invalid_e': _('Invalid credit card expiration date'),
                              'invalid_c': _('Invalid credit card security code'),})
        
        t = form.get(self.t,'').strip().lower()
        n = form.get(self.n,'').replace('-','').replace(' ','').strip()
        e = form.get(self.e,'').strip()
        for k in ('-','/','\\','.',' '): 
            e = e.replace(k, '')
        c = form.get(self.c,'').strip()
        errors = {}
        valid = False
        
        if t in self.card_info.keys():  # - type and number
            try:
                int(n)
                for prefix, length in self.card_info[t]:
                    if len(n) == length and n.startswith(prefix):
                        valid = True
                        break                
                if not (valid and self._validate_luhn(n)):
                    errors[self.n] = Invalid(self.message('invalid_n'), n)                
            except ValueError:
                errors[self.n] = Invalid(self.message('invalid_n'), n)            
        else:
            errors[self.t] = Invalid(self.message('invalid_t'), t)
        
        if len(e) == 6:                 # - validity date
            try:
                int(e)
                v_month, v_year = int(e[:2]), int(e[2:]) # - this is valid-to month/year
                e_month = (v_month % 12) + 1
                e_year = (v_year + 1) if e_month == 1 else v_year
                date_value = date(e_year, e_month, 1)
                if date_value <= date.today():
                    errors[self.e] = Invalid(self.message('invalid_e'), e)            
            except ValueError:
                errors[self.e] = Invalid(self.message('invalid_e'), e)
        else:
            errors[self.e] = Invalid(self.message('invalid_e'), e)
        
        try:                            # - security code
            int(c)
            if len(c) != self.code_info[t]:
                errors[self.c] = Invalid(self.message('invalid_c'), c)
        except ValueError:
            errors[self.c] = Invalid(self.message('invalid_c'), c)
            
        if errors:
            raise Invalid(self.message('invalid'), form, errors)
        
    def _validate_luhn(self, s):
        checksum, factor = 0, 1
        for c in s[::-1]:
            for c in str(factor * int(c)):
                checksum += int(c)
            factor = 3 - factor
        return checksum % 10 == 0        
