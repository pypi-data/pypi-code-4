# qmpy/base/query.py
from qmpy import *
import itertools
import numpy as np
from numpy.linalg import norm
import os
import sys
import random
import pprint
import re
import gzip
from collections import defaultdict
from my_strings import *

set_operators = {
        'and':'and',
        '&&':'and',
        'or':'or',
        '|':'or',
        'not':'not'}

search_operators = {
        '<':'lt','lt':'lt',
        '<=':'lte','lte':'lte',
        '>':'gt','gt':'gt',
        '>=':'gte','gte':'gte',
        '==':'exact','=':'exact',
        '!=':'ne','<>':'ne','ne':'ne',
        'contains':'contains'}

def get_model(model):
    model = model[0].upper() + model[1:].lower()
    try:
        model = getattr(sys.modules[__name__], model)
    except:
        return None
    if issubclass(model, models.Model):
        return model
    else:
        return None

def query(type='entry',
        formula='',
        search='',
        result='summary',
        skip_comp=False,
        unique=False):
    '''
    Most important function here. Governs the ability to give a search and get
    back a set of matching structures. This matching set is used as an argument
    of nearly every other function.
    '''

    model = get_model(type)
    result = model.objects.all()
    if not formula and not search:
        print 'No search criteria given, returning nothing'
        return result

    # Search on formula
    if formula:
        print formula
        formulae = parse_formula(formula)
        if any( 0 in d.values() for d in formulae):
            skip_comp = True
        f_result = Entry.objects.none()
        for comp in formulae:
            print comp
            if not skip_comp:
                name = comp_to_name(comp, special='reduce')
                if not Composition.objects.filter(name=name).exists():
                    tmpr = Entry.objects.none()
                    continue
                tmpr = Composition.objects.get(name=name).entry_set.all()
                f_result = f_result | tmpr
                continue
            ntypes = len(comp)
            tmpr = Entry.objects.all()
            for elt in comp:
                ents = Element.objects.get(symbol=elt).entry_set.all()
                nents = ents.filter(ntypes=ntypes)
                tmpr = tmpr & nents
            f_result = f_result | tmpr
        
        result = result & f_result

    # Search on traditional search criteria
    if search:
        if isinstance(search,str) or isinstance(search,unicode):
            search = search.split()
        next = 'column'
        chain = 'and'
        for s in search:
            if next == 'column':
                gen = parse_columns(s)
                next = 'operator'
            elif next == 'operator':
                operator = search_operators[s]
                next = 'value'
            elif next == 'value':
                value = s
                next = 'evaluate'
            elif next == 'chain':
                chain = set_operators[s]
                next = 'column'
            if next == 'evaluate':
                db,col = gen[0]
                if db == 'master':
                    if operator != 'ne':
                        tmpr = Entry.objects.filter(**{
                            '%s__%s' % (col,operator):value})
                    else:
                        tmpr = Entry.objects.exclude(**{
                            col:value})
                else:
                    if operator != 'ne':
                        tmpr = Entry.objects.filter(**{
                            str('%s__%s__%s' % (db,col,operator)):value})
                    else:
                        tmpr = Entry.objects.exclude(**{
                            str('%s__%s' % (db,col)):value})
                if chain == 'and':
                    result = result & tmpr
                elif chain == 'or':
                    result = result | tmpr
                elif chain == 'not':
                    result = result.exclude(pk__in=tmpr)
                next = 'chain'

    if unique:
        new_result = {}
        for r in result:
            s = cS.Structure(r.id)
            try:
                s.set_thermo('econverge')
            except:
                continue
            if s.name not in new_result:
                new_result[s.name] = [r,s]
            else:
                if s.dE < new_result[s.name][1].dE:
                    new_result[s.name] = [r,s]
        result = [ r[0] for r in new_result.values() ]

    if not result:
        print 'Nothing found!'
        return result
    else:
        return result

