# Copyright (c) 2010 NORC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import division, unicode_literals, absolute_import

from .. import Loader, Saver, register, SrcLoader, SrcSaver
from . import codes
from ..options import option, loads
from ...errors import *
from ...variables import Variable, VariableSpec
from ... import format 
from ...util import memoize, NOT_DEFINED
from threading import RLock
from decimal import Decimal
from functools import wraps

from collections import defaultdict
from itertools import izip
import re, datetime, os
import platform

 

'''@todo: Add memory cleaning support.'''

class SpssError(Exception):
    def __init__(self, msg, code):
        Exception.__init__(self, msg)
        self.code = code

class SpssWarning(SpssError):
    pass

from ctypes import *

def _check_spss_err(result):
    if result != codes.SPSS_OK:
        raise (SpssWarning if result < 0 else SpssError)(codes.messages['errors'][result], result)

def _call(func, argtypes = None, restype = _check_spss_err, returns = 'pointer'):
    if argtypes is not None:
        func.argtypes = argtypes

    func.restype = restype

    _p = None
    if returns:
        _p = []
        if argtypes:
            for r in argtypes:
                if hasattr(r, 'contents'):
                    _p.append(r._type_)

    if not _p:
        returns = None
    elif returns == 'value':
        _p = list(pointer(r()) for r in _p)

    def _exec(*args):
        if returns:
            if returns == 'value':
                _h = _p
            else:
                _h = list(pointer(r()) for r in _p)

            args = list(args) + _h

        result = func(*args)

        if restype is not _check_spss_err:
            return result

        if returns:
            if returns == 'value':
                _ret = tuple(v.contents.value for v in _h)
                return _ret[0] if len(_ret) == 1 else (_ret or None)
            elif returns == 'pointer':
                _ret = tuple(v.contents for v in _h)
                return _ret[0] if len(_ret) == 1 else (_ret or None)

    return _exec


#TODO experiment with replacing POINTER with byref to see if we can improve performance
#if platform.machine() == 'AMD64':
if platform.architecture()[0] == "32bit":
    os.environ['PATH'] = os.path.dirname(__file__) + '\\i386;' + os.environ['PATH']
    dll_folder = 'i386'
    dll_file = 'spssio32.dll'
else:
    os.environ['PATH'] = os.path.dirname(__file__) + '\\64;' + os.environ['PATH']
    dll_folder = '64'
    dll_file = 'spssio64.dll'
    
windll.LoadLibrary(os.path.join(os.path.dirname(__file__), dll_folder, dll_file))
_windll = windll.spssio32 if platform.architecture()[0] == "32bit" else windll.spssio64
_open_read = _call(_windll.spssOpenRead, [c_char_p, POINTER(c_int)], returns = 'pointer')
_open_write = _call(_windll.spssOpenWrite, [c_char_p, POINTER(c_int)], returns = 'pointer')
_close_read = _call(_windll.spssCloseRead, [c_int])
_close_write = _call(_windll.spssCloseWrite, [c_int])
_get_number_of_cases = _call(_windll.spssGetNumberofCases, [c_int, POINTER(c_long)], returns = 'value')
_get_var_names = _call(_windll.spssGetVarNames, [c_int, POINTER(c_int), POINTER(POINTER(c_char_p)), POINTER(POINTER(c_int))], returns = None)
_set_var_name = _call(_windll.spssSetVarName, [c_int, c_char_p, c_int])
_get_var_handle = _call(_windll.spssGetVarHandle, [c_int, c_char_p, POINTER(c_double)])
_free_var_names = _call(_windll.spssFreeVarNames, [POINTER(c_char_p), POINTER(c_int), c_int], returns = None)
_read_case_record = _call(_windll.spssReadCaseRecord, [c_int])
_get_value_char = _call(_windll.spssGetValueChar)
_get_value_numeric = _call(_windll.spssGetValueNumeric, [c_int, c_double, POINTER(c_double)], returns = 'value')
_set_value_char = _call(_windll.spssSetValueChar, [c_int, c_double, c_char_p])
_set_value_numeric = _call(_windll.spssSetValueNumeric, [c_int, c_double, c_double])
_get_var_print_format = _call(_windll.spssGetVarPrintFormat, [c_int, c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int)], returns = 'value')
_convert_date = _call(_windll.spssConvertDate, [c_int, c_int, c_int, POINTER(c_double)], returns = 'value')
_convert_time = _call(_windll.spssConvertTime, [c_long, c_int, c_int, c_double, POINTER(c_double)], returns = 'value')
_convert_spss_date = _call(_windll.spssConvertSPSSDate, [POINTER(c_int), POINTER(c_int), POINTER(c_int), c_double], returns = None)
_convert_spss_time = _call(_windll.spssConvertSPSSTime, [POINTER(c_long), POINTER(c_int), POINTER(c_int), POINTER(c_double), c_double], returns = None)
_get_var_print_format = _call(_windll.spssGetVarPrintFormat, [c_int, c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int)], returns = 'value')
_set_var_print_format = _call(_windll.spssSetVarPrintFormat, [c_int, c_char_p, c_int, c_int, c_int])
_get_var_write_format = _call(_windll.spssGetVarWriteFormat, [c_int, c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int)], returns = 'value')
_set_var_write_format = _call(_windll.spssSetVarWriteFormat, [c_int, c_char_p, c_int, c_int, c_int])
_set_compression = _call(_windll.spssSetCompression, [c_int, c_int])
_sysmis_val = _call(_windll.spssSysmisVal, restype = c_double)
_commit_header = _call(_windll.spssCommitHeader, [c_int])
_commit_case_record = _call(_windll.spssCommitCaseRecord, [c_int])
_get_var_label_long = _call(_windll.spssGetVarLabelLong)
_set_var_label = _call(_windll.spssSetVarLabel, [c_int, c_char_p, c_char_p])
_set_numeric_var_value_labels = _call(_windll.spssSetVarNValueLabel, [c_int, c_char_p, c_double, c_char_p])
_set_string_var_value_labels = _call(_windll.spssSetVarCValueLabel, [c_int, c_char_p, c_char_p, c_char_p])
_get_numeric_var_value_labels = _call(_windll.spssGetVarNValueLabels)
_get_string_var_value_labels = _call(_windll.spssGetVarCValueLabels)
_get_interface_encoding = _call(_windll.spssGetInterfaceEncoding, restype = c_int)
_set_interface_encoding = _call(_windll.spssSetInterfaceEncoding, [c_int])
_set_interface_encoding(codes.SPSS_ENCODING_UTF8)

def _encode(s):
    return s.encode('utf-8')

def _decode(s):
    return s.decode('utf-8')

SYSMIS = _sysmis_val()

class SpssVariable(object):
    def __init__(self, handle, var_name, numeric, length = None):
        self.__handle = handle

        self.__name = var_name
        name_encoded = _encode(var_name)
        self.numeric = numeric
        self.length = length

        self.__v_handle = _get_var_handle(self.__handle, name_encoded)
        self.type, self.digits, self.width = _get_var_print_format(self.__handle, name_encoded)

        self.__label_fetched = False
        self.__label = None
        
        #maximum of 1000 labels
        self.MAX_ARRAY_SIZE = 1000
        self.__value_labels_fetched = False
        self.__value_labels = None
        
        if not self.numeric:
            self.__buf = None

    @property
    def name(self):
        return self.__name

    def read_value(self):
        if self.numeric:
            value = _get_value_numeric(self.__handle, self.__v_handle)
            return None if value == SYSMIS else value
        else:
            if not self.__buf:
                length = (self.length) + 1
                self.__buf = create_string_buffer(length)
            _get_value_char(self.__handle, self.__v_handle, 
                            self.__buf, len(self.__buf))
            return _decode(string_at(self.__buf))

    def write_value(self, value):
        if self.numeric:
            _set_value_numeric(self.__handle, self.__v_handle, 
                               SYSMIS if value is None else value)
        else:
            _set_value_char(self.__handle, self.__v_handle, value)

    @property
    def label(self):
        if self.__label_fetched:
            return self.__label

        length = (codes.SPSS_MAX_VARLABEL) + 1
        buf = create_string_buffer(length)
        len_buf = pointer(c_int())
        try:
            _get_var_label_long(self.__handle, _encode(self.name), 
                                buf, length, len_buf)
            
            self.__label = _decode(string_at(buf))
            self.__label_fetched = True

            return self.__label
        except SpssWarning as e:
            if e.code == codes.SPSS_NO_LABEL:
                return ''

            raise e
    
    @property
    def value_labels(self):
        if self.__value_labels_fetched:
            return self.__value_labels
        
        length = codes.SPSS_MAX_VALLABELARR
        num_labels_buf = byref(c_int())
        labels_buf = (POINTER(c_char_p) * length)()
        
        if self.numeric:
            values_buf = (POINTER(c_double) * MAX_ARRAY_SIZE)()
            func = _get_numeric_var_value_label
        else:
            values_buf = (POINTER(c_char_p) * MAX_ARRAY_SIZE)()
            func = _get_string_var_value_label
        
        try:
            print 'trace'
            func(self.__handle, _encode(self.name), values_buf, 
                 labels_buf, num_labels_buf)
            
            vals = [values_buf[0][i] for i in xrange(num_labels.value)]
            lbls = [labels_buf[0][i] for i in xrange(num_labels.value)]            
            self.__value_labels = dict([(v, l) for v, l in zip(vals, lbls)])
            self.__value_labels_fetched = True
            
        except SpssWarning as e:
            raise e

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'SpssVariable(%r, %r, %s, %r)' % (self.__handle, self.name, 'numeric' if self.numeric else 'character', self.length)

@option(delete = True)
def dataset(options):
    pass

@loads
@option(default = False)
def delete_empty_strings(options):
    pass

@loads
@option(default = True)
def trim_spaces(options):
    pass

@option()
def invalid_date(options):
    pass

@option(default = 255, convert = int)
def max_string_width(options):
    pass

@option(default = 40, convert = int)
def max_int_width(options):
    pass
    if options['max_int_width'] > 40:
        raise OptionError('Can not have int width > 40 due to SPSS maximum integer limitations.')
    
@loads
@option(default = ('datetime', ))
def accept_formats(options):
    accept = set([format.lookup_format(f) for f in options['accept_formats']])
    if format.DATE in accept or format.TIME in accept:
        accept.append(format.DATETIME)
    
    for s in ('decimal', 'integer', 'datetime', 'date', 'time'):
        f = format.lookup_format(s)
        options['_accept_' + s] = (f in accept)
        accept.discard(f)
        
    if accept:
        raise OptionError('accept_formats cannot handle %s' % ' or '.join(f.key for f in accept))
    
class SpssDataset(object):
    def __init__(self, filename, mode = 'r', compression = True):
        self.__closed = False

        if not mode in ('r', 'w'):
            raise ArgumentError('Invalid mode: %s' % mode)

        self.__read = (mode == 'r')
        self.__header_written = False

        if self.__read:
            self.__handle = _open_read(filename)
            self.cases = _get_number_of_cases(self.__handle)

            count, names, types = pointer(c_int()), pointer(pointer(c_char_p())), pointer(pointer(c_int()))
            _get_var_names(self.__handle, count, names, types)

            try:
                self.variables = [SpssVariable(self.__handle, _decode(names.contents[i]), types.contents[i] == 0, types.contents[i]) for i in xrange(count.contents.value)]
            finally:
                _free_var_names(names.contents, types.contents, count.contents)
        else:
            self.__handle = _open_write(filename)
            _set_compression(self.__handle, 1 if compression else 0)
            self.variables = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.close()
        except:
            if not exc_type:
                raise

    def __iter__(self):
        try:
            while True:
                _read_case_record(self.__handle)
                yield [v.read_value() for v in self.variables]
        except SpssWarning, e:
            if e.code != codes.SPSS_FILE_END:
                raise e

    def add_variable(self, name, type=codes.SPSS_FMT_A, length=8, decimals=2, 
                     label=None, value_labels=None):
        """
        Add a SPSS variable to the SPSS dataset.
        
        @param name: The name of the variable.
        @param type: The variable type.
        @param length: The length of the variable.
        @param decimals: The number of decimals.
        @param label: The variable label.
        @param value_labels: Set variable value labels. 
                             Takes a list of tuples of the form 
                             [(value: valueLabel)]
                            
                             - [(1, 'yes'), (2, 'no')]
        """
        name_encoded = _encode(name)
        _set_var_name(self.__handle, name_encoded, 
                      length if type == codes.SPSS_FMT_A else 0)
        
        if type != codes.SPSS_FMT_A:
            _set_var_print_format(self.__handle, name_encoded, type, 
                                  decimals, length)
            _set_var_write_format(self.__handle, name_encoded, type, 
                                  decimals, length)
            length = 0
        
        if label:
            _set_var_label(self.__handle, name_encoded, _encode(label))
        
        if value_labels:
            if type == codes.SPSS_FMT_A:
                func = _set_string_var_value_labels
                val_type = c_char_p
            else:
                func = _set_numeric_var_value_labels
                val_type = c_double 
            
            for val, lbl in value_labels:
                func(self.__handle, name_encoded, val_type(val), c_char_p(lbl))
        
        self.variables.append((name, length))

    def append(self, row):
        if not self.__header_written:
            _commit_header(self.__handle)
            self.variables = [SpssVariable(self.__handle, name, length == 0, length) for name, length in self.variables]
            self.__header_written = True

        for v, value in izip(self.variables, row):
            v.write_value(value)

        _commit_case_record(self.__handle)

    @property
    def closed(self):
        return self.__closed

    def close(self):
        if self.__closed:
            return

        if self.__read:
            _close_read(self.__handle)
        else:
            _close_write(self.__handle)

        self.__closed = True

def _get_load_converters(options):
    delete_empty_strings = options['delete_empty_strings']
    trim_spaces = options['trim_spaces']
    invalid_date = options.get('invalid_date', NOT_DEFINED)

    _day, _month, _year = pointer(c_int()), pointer(c_int()), pointer(c_int())
    _, _hour, _minute, _second = pointer(c_long()), pointer(c_int()), pointer(c_int()), pointer(c_double())

    @memoize
    def _from_datetime(load):
        try:
            _convert_spss_date(_day, _month, _year, load)
            _convert_spss_time(_, _hour, _minute, _second, load)
            year = _year.contents.value
            if not (datetime.MINYEAR <= year <= datetime.MAXYEAR):
                if invalid_date == NOT_DEFINED:
                    raise LoadError('The date %s in SPSS cannot be loaded in Python (year %s)' % (load, year))
                else:
                    return invalid_date
                    
            return datetime.datetime(year, _month.contents.value, _day.contents.value, _hour.contents.value, _minute.contents.value, int(_second.contents.value))
        except SpssError, e:
            if e.code == codes.SPSS_INVALID_DATE:
                if invalid_date == NOT_DEFINED:
                    raise LoadError('SPSS contains an invalid date: %s' % load)
                else:
                    return invalid_date
            else:
                raise e

    @memoize
    def _from_date(load):
        d = _from_datetime(load)
        return None if d is None else d.date()

    @memoize
    def _from_time(load):
        d = _from_datetime(load)
        return None if d is None else d.time()

    @memoize
    def _from_string(load):
        if delete_empty_strings and load == '':
            return None

        if trim_spaces:
            load = load.rstrip()

        return load

    @memoize
    def _from_binary(load):
        if delete_empty_strings and load == '':
            return None

        if trim_spaces:
            load = load.rstrip()

        return bytes(load)

    @memoize
    def _from_integer(load):
        return int(load)

    @memoize
    def _from_decimal(load):
        return Decimal(load)

    converters = {
        'datetime' : _from_datetime,
        'date' : _from_date,
        'time' : _from_time,
        'string' : _from_string,
        'binary' : _from_binary,
        'float' : None,
        'integer' : _from_integer,
        'decimal' : _from_decimal,
        'boolean' : lambda l: bool(l),
    }

    def _convert(v, load):
        if load is None:
            return None

        key = v.format.key
        c = converters.get(key)
        if c is None:
            return load

        return c(load)

    return _convert

def _get_save_converters(v, options):
    max_string_width = options['max_string_width']
    invalid_date = options.get('invalid_date', NOT_DEFINED)
    if invalid_date:
        invalid_date = _convert_date(invalid_date.day, invalid_date.month, invalid_date.year) + _convert_time(0, invalid_date.hour, invalid_date.minute, invalid_date.second)

    def _date_handler(func):
        @wraps(func)
        def _exec(save):
            try:
                return func(save)
            except SpssError, e:
                if e.code == codes.SPSS_INVALID_DATE:
                    if invalid_date == NOT_DEFINED:
                        raise SaveError('Cannot save %s to SPSS' % save)
                    else:
                        return invalid_date
                else:
                    raise e

        return _exec

    @memoize
    @_date_handler
    def _to_datetime(save):
        return _convert_date(save.day, save.month, save.year) + _convert_time(0, save.hour, save.minute, save.second)

    @memoize
    @_date_handler
    def _to_date(save):
        return _convert_date(save.day, save.month, save.year)

    @memoize
    @_date_handler
    def _to_time(save):
        return _convert_time(0, save.hour, save.minute, save.second)

    def _to_boolean(save):
        return 1 if save else 0

    @memoize
    def _to_string(save):
        if len(save) > max_string_width:
            raise SaveError('Cannot save "%s" to %s (it exceeds the maximum string width of %s : %s' % (save, v.name, v.rules.length, len(save)))

        return save

    converters = {
        'boolean' : _to_boolean,
        'datetime' : _to_datetime,
        'date' : _to_date,
        'time' : _to_time,
        'string' : _to_string,
        'binary' : _to_string,
        'float' : None,
        'integer' : None,
        'decimal' : None,
    }

    def _convert(v, save):
        key = v.format.key
        if save is None:
            if key in ('string', 'binary'):
                return ''
            else:
                return None

        c = converters.get(key)
        if c is None:
            return save

        return c(save)

    return _convert

_locks = defaultdict(RLock)
class SpssHandler(SrcLoader, SrcSaver):
    id = 'cardsharp.loaders.spss'
    formats = ['spss', ]

    def list_datasets(self, options):
        return None

    def get_dataset_info(self, options):
        filename = options['source']

        with _locks[filename]:
            with SpssDataset(filename) as dataset:
                var_spec = []
                for var in dataset.variables:
                    if var.length:
                        v_def = Variable(var.name, 'string', length = var.length)
                    else:
                        if var.type in (codes.SPSS_FMT_DATE, codes.SPSS_FMT_TIME, codes.SPSS_FMT_DATE_TIME, codes.SPSS_FMT_ADATE, codes.SPSS_FMT_EDATE, codes.SPSS_FMT_SDATE, codes.SPSS_FMT_JDATE, codes.SPSS_FMT_DTIME):
                            if not options['_accept_datetime']:
                                v_def = Variable(var.name, 'float')
                            elif not var.type == codes.SPSS_FMT_DATE_TIME and options['_accept_date']:
                                v_def = Variable(var.name, 'date')
                            else:
                                v_def = Variable(var.name, 'datetime')
                        elif var.type == codes.SPSS_FMT_F:
                            if options['_accept_integer'] and var.digits == 0:
                                v_def = Variable(var.name, 'integer')
                            elif options['_accept_decimal']:
                                v_def = Variable(var.name, 'decimal', decimals = var.digits)
                            else:
                                v_def = Variable(var.name, 'float')
                        else:
                            raise FormatError('Unknown SPSS format: ' + codes.messages['formats'][var.type])
                        
                    v_def.label = var.label

                    var_spec.append(v_def)

                options['_cases'] = dataset.cases
                options['_variables'] = VariableSpec(var_spec)
                options['format'] = 'spss'

    def can_load(self, options):
        if options.get('format') == 'spss':
            return 5000

        f = options.get('source')
        if f:
            try:
                handle = _open_read(f)
            except SpssError as e:
                if e.code == codes.SPSS_INVALID_FILE:
                    return 0
                else:
                    raise e
            else:
                _close_read(handle)
                return 5000

        return 0

    class loader(Loader):
        def rows(self):
            filename = self.options['source']

            with _locks[filename]:
                with SpssDataset(filename) as dataset:
                    convert = _get_load_converters(self.options)
                    for row in self.options['_filter'].filter(dataset):
                        yield [convert(v, value) for v, value in self.options['_variables'].pair_filter(row)]

    def can_save(self, options):
        if options.get('format') == 'spss':
            return 5000

        return 0

    class saver(Saver):
        def rows(self):
            filename = self.options['source']

            with _locks[filename]:
                with SpssDataset(filename, mode = 'w') as dataset:
                    for v in self.options['_variables'].filter():
                        name = self.options['_variables'].original(v)
                        key = v.format.key
                        if key == 'string':
                            string_width = self.options['max_string_width']
                            length = v.rules.length or string_width
                            if length > string_width and not v.flags.string_width_override:                                
                                raise SaveError('Cannot save variable (%s) with a length of %s (maximum width %s)' % (v.name, length, string_width))
                            dataset.add_variable(name, codes.SPSS_FMT_A, length, 
                                                 label = v.label,
                                                 value_labels=v.value_labels)
                        elif key == 'float':
                            l = v.rules.length
                            
                            if l > self.options['max_int_width']:                                
                                raise SaveError('Cannot save variable (%s) with a length of %s (maximum width %s)' % (v.name, length, int_width))
                            dataset.add_variable(name, codes.SPSS_FMT_F,
                                                 length = l or 8,
                                                 decimals = v.rules.scale or 2,
                                                 label = v.label,
                                                 value_labels=v.value_labels)
                        elif key == 'date':
                            dataset.add_variable(name, codes.SPSS_FMT_DATE, 11, 
                                                 0, label = v.label,
                                                 value_labels=v.value_labels)
                        elif key == 'time':
                            dataset.add_variable(name, codes.SPSS_FMT_TIME, 15, 
                                                 0, label = v.label,
                                                 value_labels=v.value_labels)
                        elif key == 'boolean':
                            dataset.add_variable(name, codes.SPSS_FMT_F, 1, 0, 
                                                 label = v.label,
                                                 value_labels=v.value_labels)
                        elif key == 'datetime':
                            dataset.add_variable(name, codes.SPSS_FMT_DATE_TIME, 
                                                 23, 0, label = v.label,
                                                 value_labels=v.value_labels)
                        elif key == 'integer':
                            l = v.rules.length
                            
                            if l > self.options['max_int_width']:                                
                                raise SaveError('Cannot save variable (%s) with a length of %s (maximum width %s)' % (v.name, length, int_width))
                            dataset.add_variable(name, codes.SPSS_FMT_F, 
                                                 length = l or 8, 
                                                 decimals = v.rules.scale or 0, 
                                                 label = v.label,
                                                 value_labels=v.value_labels)
                        elif key == 'decimal':
                            l = v.rules.length
                            if l > self.options['max_int_width']:                                
                                raise SaveError('Cannot save variable (%s) with a length of %s (maximum width %s)' % (v.name, length, int_width))
                            dataset.add_variable(name, codes.SPSS_FMT_F,
                                                 length = l or 8, 
                                                 decimals = v.rules.scale or 2, 
                                                 label = v.label,
                                                 value_labels=v.value_labels)
                        else:
                            raise FormatError('Cannot save %s to SPSS' + key)

                    convert = _get_save_converters(v, self.options)
                    while True:
                        r = (yield)
                        r = [convert(v, x) for v, x in self.options['_variables'].pair_filter(r)]
                        dataset.append(r)

register(SpssHandler())