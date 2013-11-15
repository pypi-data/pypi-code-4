#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

from formv.validators.base import VBase
from formv.exception import Invalid 
from formv.utils import empty, extract_text as _
from formv.utils.compat import iteritems

__all__ = ('VSchema',)

class VSchema(VBase):
    """ HTML schema validator. 

    Parameters as follows:
    
    allow_extra_keys
        Validator has less keys than form, allow extra keys. Boolean.  
    allow_missing_keys
        Validator has more keys than form, allow keys to be missing. Boolean.        
    remove_extra_keys                
        Validator has less keys than form, remove extra keys. Boolean.
    replace_missing_key
        Validator has more keys than form, missing keys will be replaced 
        with missing_key_value value. Boolean.
    missing_key_value
        Replacement value for missing keys
    replace_empty_value
        Empty values will be replaced with values from empty_values. Boolean.
    empty_values={},
        Dictionary of values to be used if the value is empty. See 
        examples/reuse_files.py for an example of how this can be used to reuse  
        an uploaded file if file validation has succeeded, but overall form 
        validation has failed
    remove_empty_keys
        Remove empty keys indicator. Boolean.
    
    Note that chain validation is sorting chains by key prior to 
    execution so you can introduce key-based dependencies.
    
    Example of key-based dependency:
    
    class WebForm(VSchema):   
             
        fields = {        
            'postcode_origin': VString(),
            'postcode_destination': VString(),
            'country': VCountry(required=True, mode='by-name'),
        }
                
        # note the keys below, 'z-geodist' has to be executed last   
        # as it depends on 'origin' and 'destination' keys
        
        chains = {    
            # generates (latitude, longitude) pair on success
            'origin': VPostcode(country_field='country',             
                                postcode_field='postcode_origin'),
                                
            # generates (latitude, longitude) pair on success
            'destination': VPostcode(country_field='country', 
                                     postcode_field='postcode_destination'),
            
            # uses (latitude, longitude) pairs to calculate geo-distance
            'z-geodist': VGeoDistance(origin_field='origin', 
                                      destination_field='destination'),
        }
    """
    
    messages = {'form_errors': _('The form has errors, please correct them before submitting'),
                'bad_fieldname': _('Field-name "form" is reserved, can\'t be used in forms'),
                'extra_keys': _('Extra fields are not allowed'),
                'missing_keys': _('Missing fields are required'),}
    
    fields = {}
    chains = {}
    
    def __init__(self, allow_extra_keys=False, 
                       allow_missing_keys=False,                       
                       remove_extra_keys=False,                
                       replace_missing_key=False,
                       missing_key_value=None,
                       replace_empty_value=False,
                       empty_values={},
                       remove_empty_keys=True):
        
        self.allow_extra_keys = allow_extra_keys
        self.allow_missing_keys = allow_missing_keys
        self.remove_extra_keys = remove_extra_keys
        self.replace_missing_key = replace_missing_key
        self.missing_key_value = missing_key_value
        self.replace_empty_value = replace_empty_value
        self.empty_values = empty_values
        self.remove_empty_keys = remove_empty_keys
    
    def validate(self, form):
        assert hasattr(form, 'items'), _('Form has to be a dict-like object')

        if hasattr(form, 'mixed'):
            form = form.mixed()

        errors = {'form':[]}
        
        for k in (form, self.fields, self.chains): 
            if 'form' in k.keys():
                errors['form'].append(self.message('bad_fieldname'))
                break
        
        f_keys = set(form.keys())               # - form keys
        v_keys = set(self.fields.keys())        # - validator keys
        extra_f_keys = f_keys - v_keys          # - extra form keys
        extra_v_keys = v_keys - f_keys          # - extra validator keys
        
        if self.remove_extra_keys:
            for k in extra_f_keys:
                del form[k]
            extra_f_keys = set()
        
        if self.replace_empty_value:            # - defaults for empty values
            for k, value in iteritems(form):   
                if empty(value):
                    form[k] = self.empty_values.get(k)
        
        if self.replace_missing_key:            # - defaults for missing keys
            for k in extra_v_keys:
                form[k] = self.missing_key_value
            extra_v_keys = set()
        
        if extra_f_keys:                        # - form has more keys than validator
            if not self.allow_extra_keys:
                errors['form'].append(self.message('extra_keys'))
        
        if extra_v_keys:                        # - validator has more keys than form 
            if not self.allow_missing_keys:
                errors['form'].append(self.message('missing_keys'))
        
        if not errors['form']:                  # - form setup had no errors, remove key 
            del errors['form']

        for k, v in iteritems(form):           # - fields validation -            
            ftype = self.fields.get(k)
            if ftype:
                try:
                    form[k] = ftype.validate(v)
                except Invalid as e:
                    errors[k] = e.message

        for k in sorted(self.chains.keys()):    # - chains validation -
            v = self.chains[k]
            try:
                form[k] = v.validate(form) 
            except Invalid as e:
                errors[k] = e.message
                if isinstance(e.errors, dict):
                    for ek, ev in iteritems(e.errors):
                        errors[ek] = ev.message
        
        if self.remove_empty_keys:               # - remove empty form keys
            for k in [k for k in form.keys() if empty(k)]:  
                form.pop(k, None)

        if errors: 
            raise Invalid(self.message('form_errors'), form, errors)
        
        return form
    