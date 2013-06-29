# Copyright Abel Deuring 2012
# python-ptp-chdk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.

"""Parse the ptp.h file and build C source file with data structures
that can be used to create Python C classes representing constants
defined in ptp.h.
"""

import re

# VERY limited: No whitespace allowed in the definition. But should
# be good enough to find integer constants.
define_re = re.compile(r'^\s*#define\s+([^\s]+)\s+([^\s]+)')
enum_re = re.compile(r'enum\s+(([A-Za-z0-9_]+)\s+{(.*?)})', re.DOTALL)
enum_without_comments_1 = re.compile(r'//.*$', re.MULTILINE)
enum_without_comments_2 = re.compile(r'/\*.*?\*/')
enum_no_spaces = re.compile(r'\s+')

def parse_ptp_h(filenames):
    """Find '#define ...' lines in the given file and return a sequence
    of tuples (defined_name, defined_value).

    Also parse enum definitions.
    """
    result = []
    for name in filenames:
        for line in open(name):
            mo = define_re.search(line.strip())
            if mo:
                result.append(mo.groups())
        contents = open(name).read()
        for ignore, name, enum_inner in enum_re.findall(contents):
            enum_inner = enum_without_comments_1.sub('', enum_inner)
            enum_inner = enum_without_comments_2.sub('', enum_inner)
            enum_inner = enum_no_spaces.sub('', enum_inner)
            if enum_inner[-1] == ',':
                enum_inner = enum_inner[:-1]
            value_strings = enum_inner.split(',')
            current_value = 0
            for element in value_strings:
                definition = element.split('=')
                if len(definition) > 1:
                    current_value = int(definition[1])
                else:
                    current_value += 1
                result.append((definition[0], current_value))
    return result

def filter_by_prefix(prefix, definitions):
    """Filter the definitions by their prefix; remove prefix from name."""
    cut = len(prefix)
    filtered = [d for d in definitions if d[0].startswith(prefix)]
    return [(name[cut:], value) for name, value in filtered]


constant_info_entry_template = """\
  {"ptp.%s", "%s", NULL, %s_data,
   init_int_constant_class_dict},
"""

constant_info_table_template = """\
static struct {
  char *full_name;
  char *name;
  char *doc;
  void *data;
  init_dict_func *init_dict;
} constant_info[] = {
%s
  {NULL}
};
"""

constant_int_template = """static int_const_t %s_data[] = {
%s
  {NULL,}
};

"""

def constants_from_int(classname, prefix, definitions, out):
    """Generate the definition of a static int_const_t NAME[] array.

    Returns an entry for constant_info
    """
    defs = filter_by_prefix(prefix, definitions)
    def_lines = ['  {"%s", %s},' % (name, value) for name, value in defs]
    def_lines = '\n'.join(def_lines)
    out.write(constant_int_template % (classname, def_lines))
    return constant_info_entry_template % (classname, classname, classname)

def constants_from_header_file(header_file_names, out, info):
    """Parse the C header files header_file_names, write into out
    definitions for classes that are "constant containers".

    info: A sequence of (classname, prefix) tuples.
    classname is the name of Python class that will contain the
    constants; prefix is the common prefix of the #define name
    in the header file.
    """
    defs = parse_ptp_h(header_file_names)
    classinfo = []
    for classname, prefix in info:
        classinfo.append(constants_from_int(classname, prefix, defs, out))
    out.write(constant_info_table_template % '\n'.join(classinfo))


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        out = sys.stdout
    else:
        out = open(sys.argv[2], 'w')

    info = [
        ('Vendor', 'PTP_VENDOR_'),
        ('OperationCode', 'PTP_OC_'),
        ('ResponseCode', 'PTP_RC_'),
        ('PTPErrorID', 'PTP_ERROR_'),
        ('EventCode', 'PTP_EC_'),
        ('ObjectFormat', 'PTP_OFC_'),
        ('AssociationType', 'PTP_AT_'),
        ('ProtectionStatus', 'PTP_PS_'),
        ('StorageType', 'PTP_ST_'),
        ('FileSystemType', 'PTP_FST_'),
        ('AccessCapability', 'PTP_AC_'),
        ('PropertyID', 'PTP_DPC_'),
        ('CHDKScriptType', 'PTP_CHDK_SL_'),
        ('CHDKScriptStatus', 'PTP_CHDK_SCRIPT_STATUS_'),
        ('CHDKMessageType', 'PTP_CHDK_S_MSGTYPE_'),
        ('CHDKMessageStatus', 'PTP_CHDK_S_MSGSTATUS_'),
        ('LiveViewFlags', 'LV_TFR_')
        ]
    constants_from_header_file(sys.argv[1:], out, info)

    if out != sys.stdout:
        out.close()
