# Copyright (c) 2013, Calxeda Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# * Neither the name of Calxeda Inc. nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

import struct
from functools import partial
import defs.variables
import defs.types

_marshaling_funcs = {}

def marshal_basic_type(size_str, data):
    return struct.pack('<' + size_str, data)


def marshal_struct(members, data):
    value = ''
    for (c_name, data_type, long_name, default) in members:
        if default == None:
            d = data[long_name]
        else:
            d = data.get(long_name, default)
        value += _marshaling_funcs[data_type](d)
    return value


def marshal_array(member_type, length, data):
    value = ''
    for i in range(length):
        if(i < len(data)):
            value += _marshaling_funcs[member_type](data[i])
        else:
            print "[WARNING] array too short, padding with \\0"
            value += _marshaling_funcs[member_type]('\0')
    return value


def marshal_enum(size, constants, data):
    if type(data) == int:
        val = data
    else:
        val = constants[data]
    size_str = defs.types.basic_data_types[size]
    return struct.pack('<' + size_str, val)

def marshal_string(length, data):
    if(len(data) < length):
        data += '\0' * (length - len(data))
    elif(len(data) > length):
        print "[FATAL] string \"%s\" is too long!" % data
        sys.exit(1)
    return struct.pack('<' + str(length) + 's', data)

def init_marshaling_funcs():
    # switch for data type
    basic_type_curry_funcs = {
         'struct' : lambda td: partial(marshal_struct, td['members']),
         'array' : lambda td:
            partial(marshal_array, td['member_type'], td['length']),
         'enum' : lambda td: partial(marshal_enum, td['size'], td['constants']),
         'string' : lambda td: partial(marshal_string, td['length'])
        }
    # add basic types to switch
    for (name, size_str) in defs.types.basic_data_types.iteritems():
        basic_type_curry_funcs[name] = lambda ignore: partial(marshal_basic_type, size_str)

    # curry marshaling funcs with the user defined types
    for (name, td) in defs.types.data_types.iteritems():
        _marshaling_funcs[name] = basic_type_curry_funcs[td['type']](td)

    # add basic types
    for (name, size_str) in defs.types.basic_data_types.iteritems():
        _marshaling_funcs[name] = partial(marshal_basic_type, size_str)


# returns a dict mapping variables to functions that will marshal their data
def get_marshal_dict():
    marshal_dict = {}
    init_marshaling_funcs()
    for (var_name, desc) in defs.variables.var_defs.iteritems():
        marshal_dict[var_name] = _marshaling_funcs[desc['type']]
    return marshal_dict


# creates a list of all the valid symbols to use in a cfg file
def get_symbols():
    symbols = {}
    for (name, definition) in defs.types.data_types.iteritems():
        # no need to add the type name, they should not appear in cfg
        if definition['type'] == 'struct':
            add_struct_members(symbols, definition)
        elif definition['type'] == 'enum':
            add_enum_constants(symbols, definition)
    for v in defs.variables.var_defs.keys():
        symbols[v] = v
    return symbols


def add_struct_members(symbols, definition):
    for (c_name, data_type, long_name, default) in definition['members']:
        symbols[long_name] = long_name


def add_enum_constants(symbols, definition):
    for (name, val) in definition['constants'].iteritems():
        symbols[name] = name


# returns a dict of key to int id mappings
def get_key_nums():
    key_nums = {}
    for (name, info) in defs.variables.var_defs.iteritems():
        key_nums[name] = info['id']
    return key_nums
