# -*- coding: utf-8 -*-


from functools import partial


class ValidationError(Exception):
    pass


class Schema(object):

    @classmethod
    def from_dict(cls, dict_scheme, **kwargs):
        if type(dict_scheme) is not dict:
            raise TypeError(
                'Dict schema must be a dict and follow valid format.')

        s = Schema(**kwargs)
        for f_name, modifiers in dict_scheme.iteritems():
            field = getattr(s, f_name)
            for m in modifiers:
                if type(m) is str:
                    getattr(field, m)()
                elif type(m) is tuple:
                    getattr(field, m[0])(*m[1:])
        return s

    def __init__(self, match=[], require=[], blank=[],
                 alts=[], extras='discard', force_unicode=True,
                 strip_missing=True, strip_blank=True):

        self._filters_by_names = {}
        self._names_by_filters = {}

        self._field_options = {}
        self._field_options['match'] = match
        self._field_options['require'] = require
        self._field_options['blank'] = blank
        self._field_options['alts'] = alts
        self._field_options['extras'] = extras
        self._field_options['force_unicode'] = force_unicode
        self._field_options['strip_missing'] = strip_missing
        self._field_options['strip_blank'] = strip_blank

    def __getattr__(self, attr):
        return self.add_filter_chain(attr, FilterChain(self))

    @property
    def errors(self):
        return {ns[0]: fc.errors
                for fc, ns in self._names_by_filters.iteritems()}

    @property
    def valid(self):
        return all([fc.valid for fc in self._names_by_filters.keys()])

    @property
    def results(self):
        if self._field_options['strip_missing']:
            r = {}
            filters = self._matched.values()
            for f in filters:
                if f.valid:
                    name = self._names_by_filters[f][0]
                    r[name] = f.result
        else:
            r = {
                names[0]: filter_chain.result
                for filter_chain, names in self._names_by_filters.iteritems()
                if filter_chain.valid
            }

        if self._field_options['strip_blank']:
            r = {
                name: result
                for name, result in r.iteritems()
                if result is not None
            }

        return r

    def add_filter_chain(self, name, filter_chain):
        self._filters_by_names[name] = filter_chain

        try:
            existing_names = self._names_by_filters[filter_chain]
        except KeyError:
            existing_names = []

        existing_names.append(name)
        self._names_by_filters[filter_chain] = existing_names
        setattr(self, name, filter_chain)
        return filter_chain

    def validate(self, data_dict, **kwargs):
        self._apply_alternate_fields()

        present_names = set(data_dict.keys())
        defined_names = set(self._filters_by_names.keys())

        matched_names = defined_names.intersection(present_names)
        unmatched_names = defined_names.difference(present_names)

        missing_names = defined_names.intersection(unmatched_names)

        matched_filters_by_name = {
            n: fc for n, fc in self._filters_by_names.iteritems()
            if n in matched_names
        }
        self._matched = matched_filters_by_name

        missing_filters = set([
            self._filters_by_names[n] for n in missing_names
        ]).difference(set(matched_filters_by_name.values()))

        missing_filters_by_name = {}
        for filter_chain in missing_filters:
            names = self._names_by_filters[filter_chain]
            missing_filters_by_name[names[0]] = filter_chain

        self._missing = missing_filters_by_name

        if self._field_options['extras'] == 'discard':
            data_dict = {k: data_dict[k] for k in matched_names}

        if self._field_options['force_unicode']:
            data_dict = self._cast_to_unicode(data_dict)

        self._apply_required_fields(missing_filters_by_name)
        self._apply_blank_fields(matched_filters_by_name)
        self._apply_matching_fields(matched_filters_by_name)

        self._invalidate_missing_if_required(missing_filters_by_name)
        self._invalidate_if_not_matching(matched_filters_by_name, data_dict)

        for name, filter_chain in matched_filters_by_name.iteritems():
            filter_chain.validate(data_dict[name])

    def _apply_required_fields(self, filters_by_name):
        require_option = self._field_options['require']
        for name, filter_chain in filters_by_name.iteritems():
            if require_option == 'all':
                filter_chain.require(True)
            elif require_option == 'none':
                filter_chain.require(False)
            elif name in require_option:
                filter_chain.require(True)

    def _apply_blank_fields(self, filters_by_name):
        blank_option = self._field_options['blank']
        for name, filter_chain in filters_by_name.iteritems():
            if blank_option == 'all':
                filter_chain.blank(True)
            elif blank_option == 'none':
                filter_chain.blank(False)
            elif name in blank_option:
                filter_chain.blank(True)

    def _apply_matching_fields(self, filters_by_name):
        match_groups = self._field_options['match']
        for match_group in match_groups:
            first = list(match_group)[0]
            rest = list(match_group)[1:]
            filter_chain = filters_by_name[first]
            for n in rest:
                other = filters_by_name[n]
                filter_chain.match(other)

    def _apply_alternate_fields(self):
        alt_groups = self._field_options['alts']
        filters = self._filters_by_names
        for g in alt_groups:
            fc = filters[g[0]]
            alt_names = g[1:]
            for n in alt_names:
                fc.alt(n)

    def _cast_to_unicode(self, data_dict):

        def _string_cast(value):
            if type(value) is str:
                return unicode(value)
            return value

        new_dict = {}

        for k, v in data_dict.iteritems():
            new_k = _string_cast(k)
            if type(v) is (set):
                v = dict(v)
            if type(v) is (dict):
                new_dict[new_k] = self._cast_to_unicode(v)
                continue
            elif type(v) is list:
                new_dict[new_k] = [_string_cast(i) for i in v]
            elif type(v) is tuple:
                new_dict[new_k] = tuple([_string_cast(i) for i in v])
            else:
                new_dict[new_k] = _string_cast(v)
        return new_dict

    def _invalidate_missing_if_required(self, filters_by_name):
        for name, filter_chain in filters_by_name.iteritems():
            filter_chain._ran = True

            if filter_chain.required:
                filter_chain._errors.append('This field cannot be missing.')
            else:
                filter_chain._valid = True

    def _invalidate_if_not_matching(self, filters_by_name, data_dict):
        for name, filter_chain in filters_by_name.iteritems():
            must_match = filter_chain.must_match

            for m in must_match:
                if type(m) is not FilterChain:
                    match_name = m
                    m = filters_by_name[m]
                else:
                    names = self._names_by_filters[m]
                    match_name = [
                        n for n in names if n in filters_by_name.keys()][0]

                if data_dict[name] == data_dict[match_name]:
                    continue

                filter_chain._ran = True
                filter_chain._errors.append(
                    'This field must match: %s' % (match_name))
                m._ran = True
                m._errors.append(
                    'This field must match: %s' % (name))

    def reset(self):
        filters = self._names_by_filters.keys()
        [f.reset() for f in filters]


class FilterChain(object):

    def __init__(self, schema):
        self._schema = schema
        self._filters = []
        self._required = None
        self._blank = None
        self._match = []

        self.reset()

    @property
    def valid(self):
        return self._valid

    @property
    def errors(self):
        return self._errors

    @property
    def original(self):
        return self._original_value

    @property
    def result(self):
        return self._value

    @property
    def required(self):
        if self._required is None:
            return False
        return self._required

    @property
    def blank_allowed(self):
        if self._blank is None:
            return False
        return self._blank

    @property
    def must_match(self):
        return self._match

    def reset(self):
        self._ran = False
        self._valid = False
        self._errors = []
        self._original_value = self._value = None

    def validate(self, value):
        if not self._ran:
            self._original_value = self._value = value

            if self._value == '':
                self._value = None

            if self._value is None and not self.blank_allowed:
                self._errors.append('This field cannot be blank.')
            else:
                try:
                    for f in self._filters:
                        self._value = f.run(self._value)
                except ValidationError as e:
                    self._valid = False
                    self._errors.append(str(e))
                else:
                    self._valid = True

            self._ran = True

        return self._valid

    def require(self, value=True):
        if self._required is None:
            self._required = value
        return self

    def blank(self, value=True):
        if self._blank is None:
            self._blank = value
        return self

    def match(self, *filter_chains):
        if not self._match:
            self._match = filter_chains
        return self

    def alt(self, alt_name):
        self._schema.add_filter_chain(alt_name, self)
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        fxn, pre, post = lookup(name)
        if not fxn:
            raise RuntimeError('Filter %s is undefined' % name)

        if pre:
            pref = Filter(self, pre)
            self._filters.append(pref)

        f = Filter(self, fxn)
        self._filters.append(f)

        if post:
            postf = Filter(self, post)
            self._filters.append(postf)

        return f


class Filter(object):

    def __init__(self, filter_chain, fxn):
        self._filter_chain = filter_chain
        self._validation_fxn = fxn

    def __call__(self, *args, **kwargs):
        partial_fxn = partial(self._validation_fxn, *args, **kwargs)
        partial_fxn.__name__ = self._validation_fxn.__name__
        self._validation_fxn = partial_fxn
        return self._filter_chain

    def __repr__(self):
        return '[Filter - %r]' % self._validation_fxn.__name__

    def run(self, value):
        processed = self._validation_fxn(_value=value)
        return processed


from filters import lookup
