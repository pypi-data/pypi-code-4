# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)



DESCRIPTOR = descriptor.FileDescriptor(
  name='ql2.proto',
  package='',
  serialized_pb='\n\tql2.proto\"\'\n\x0cVersionDummy\"\x17\n\x07Version\x12\x0c\n\x04V0_1\x10\xb6\xf4\x86\xfb\x03\"\xec\x01\n\x05Query\x12\x1e\n\x04type\x18\x01 \x01(\x0e\x32\x10.Query.QueryType\x12\x14\n\x05query\x18\x02 \x01(\x0b\x32\x05.Term\x12\r\n\x05token\x18\x03 \x01(\x03\x12\x16\n\x07noreply\x18\x04 \x01(\x08:\x05\x66\x61lse\x12(\n\x0eglobal_optargs\x18\x06 \x03(\x0b\x32\x10.Query.AssocPair\x1a,\n\tAssocPair\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x12\n\x03val\x18\x02 \x01(\x0b\x32\x05.Term\".\n\tQueryType\x12\t\n\x05START\x10\x01\x12\x0c\n\x08\x43ONTINUE\x10\x02\x12\x08\n\x04STOP\x10\x03\"`\n\x05\x46rame\x12\x1e\n\x04type\x18\x01 \x01(\x0e\x32\x10.Frame.FrameType\x12\x0b\n\x03pos\x18\x02 \x01(\x03\x12\x0b\n\x03opt\x18\x03 \x01(\t\"\x1d\n\tFrameType\x12\x07\n\x03POS\x10\x01\x12\x07\n\x03OPT\x10\x02\"#\n\tBacktrace\x12\x16\n\x06\x66rames\x18\x01 \x03(\x0b\x32\x06.Frame\"\xfe\x01\n\x08Response\x12$\n\x04type\x18\x01 \x01(\x0e\x32\x16.Response.ResponseType\x12\r\n\x05token\x18\x02 \x01(\x03\x12\x18\n\x08response\x18\x03 \x03(\x0b\x32\x06.Datum\x12\x1d\n\tbacktrace\x18\x04 \x01(\x0b\x32\n.Backtrace\"\x83\x01\n\x0cResponseType\x12\x10\n\x0cSUCCESS_ATOM\x10\x01\x12\x14\n\x10SUCCESS_SEQUENCE\x10\x02\x12\x13\n\x0fSUCCESS_PARTIAL\x10\x03\x12\x10\n\x0c\x43LIENT_ERROR\x10\x10\x12\x11\n\rCOMPILE_ERROR\x10\x11\x12\x11\n\rRUNTIME_ERROR\x10\x12\"\xa0\x02\n\x05\x44\x61tum\x12\x1e\n\x04type\x18\x01 \x01(\x0e\x32\x10.Datum.DatumType\x12\x0e\n\x06r_bool\x18\x02 \x01(\x08\x12\r\n\x05r_num\x18\x03 \x01(\x01\x12\r\n\x05r_str\x18\x04 \x01(\t\x12\x17\n\x07r_array\x18\x05 \x03(\x0b\x32\x06.Datum\x12\"\n\x08r_object\x18\x06 \x03(\x0b\x32\x10.Datum.AssocPair\x1a-\n\tAssocPair\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x13\n\x03val\x18\x02 \x01(\x0b\x32\x06.Datum\"T\n\tDatumType\x12\n\n\x06R_NULL\x10\x01\x12\n\n\x06R_BOOL\x10\x02\x12\t\n\x05R_NUM\x10\x03\x12\t\n\x05R_STR\x10\x04\x12\x0b\n\x07R_ARRAY\x10\x05\x12\x0c\n\x08R_OBJECT\x10\x06*\x07\x08\x90N\x10\xa1\x9c\x01\"\xcf\x07\n\x04Term\x12\x1c\n\x04type\x18\x01 \x01(\x0e\x32\x0e.Term.TermType\x12\x15\n\x05\x64\x61tum\x18\x02 \x01(\x0b\x32\x06.Datum\x12\x13\n\x04\x61rgs\x18\x03 \x03(\x0b\x32\x05.Term\x12 \n\x07optargs\x18\x04 \x03(\x0b\x32\x0f.Term.AssocPair\x1a,\n\tAssocPair\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x12\n\x03val\x18\x02 \x01(\x0b\x32\x05.Term\"\xa3\x06\n\x08TermType\x12\t\n\x05\x44\x41TUM\x10\x01\x12\x0e\n\nMAKE_ARRAY\x10\x02\x12\x0c\n\x08MAKE_OBJ\x10\x03\x12\x07\n\x03VAR\x10\n\x12\x0e\n\nJAVASCRIPT\x10\x0b\x12\t\n\x05\x45RROR\x10\x0c\x12\x10\n\x0cIMPLICIT_VAR\x10\r\x12\x06\n\x02\x44\x42\x10\x0e\x12\t\n\x05TABLE\x10\x0f\x12\x07\n\x03GET\x10\x10\x12\x06\n\x02\x45Q\x10\x11\x12\x06\n\x02NE\x10\x12\x12\x06\n\x02LT\x10\x13\x12\x06\n\x02LE\x10\x14\x12\x06\n\x02GT\x10\x15\x12\x06\n\x02GE\x10\x16\x12\x07\n\x03NOT\x10\x17\x12\x07\n\x03\x41\x44\x44\x10\x18\x12\x07\n\x03SUB\x10\x19\x12\x07\n\x03MUL\x10\x1a\x12\x07\n\x03\x44IV\x10\x1b\x12\x07\n\x03MOD\x10\x1c\x12\n\n\x06\x41PPEND\x10\x1d\x12\t\n\x05SLICE\x10\x1e\x12\x08\n\x04SKIP\x10\x46\x12\t\n\x05LIMIT\x10G\x12\x0b\n\x07GETATTR\x10\x1f\x12\x0c\n\x08\x43ONTAINS\x10 \x12\t\n\x05PLUCK\x10!\x12\x0b\n\x07WITHOUT\x10\"\x12\t\n\x05MERGE\x10#\x12\x0b\n\x07\x42\x45TWEEN\x10$\x12\n\n\x06REDUCE\x10%\x12\x07\n\x03MAP\x10&\x12\n\n\x06\x46ILTER\x10\'\x12\r\n\tCONCATMAP\x10(\x12\x0b\n\x07ORDERBY\x10)\x12\x0c\n\x08\x44ISTINCT\x10*\x12\t\n\x05\x43OUNT\x10+\x12\t\n\x05UNION\x10,\x12\x07\n\x03NTH\x10-\x12\x16\n\x12GROUPED_MAP_REDUCE\x10.\x12\x0b\n\x07GROUPBY\x10/\x12\x0e\n\nINNER_JOIN\x10\x30\x12\x0e\n\nOUTER_JOIN\x10\x31\x12\x0b\n\x07\x45Q_JOIN\x10\x32\x12\x07\n\x03ZIP\x10H\x12\r\n\tCOERCE_TO\x10\x33\x12\n\n\x06TYPEOF\x10\x34\x12\n\n\x06UPDATE\x10\x35\x12\n\n\x06\x44\x45LETE\x10\x36\x12\x0b\n\x07REPLACE\x10\x37\x12\n\n\x06INSERT\x10\x38\x12\r\n\tDB_CREATE\x10\x39\x12\x0b\n\x07\x44\x42_DROP\x10:\x12\x0b\n\x07\x44\x42_LIST\x10;\x12\x10\n\x0cTABLE_CREATE\x10<\x12\x0e\n\nTABLE_DROP\x10=\x12\x0e\n\nTABLE_LIST\x10>\x12\x0b\n\x07\x46UNCALL\x10@\x12\n\n\x06\x42RANCH\x10\x41\x12\x07\n\x03\x41NY\x10\x42\x12\x07\n\x03\x41LL\x10\x43\x12\x0b\n\x07\x46OREACH\x10\x44\x12\x08\n\x04\x46UNC\x10\x45\x12\x07\n\x03\x41SC\x10I\x12\x08\n\x04\x44\x45SC\x10J*\x07\x08\x90N\x10\xa1\x9c\x01')



_VERSIONDUMMY_VERSION = descriptor.EnumDescriptor(
  name='Version',
  full_name='VersionDummy.Version',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='V0_1', index=0, number=1063369270,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=29,
  serialized_end=52,
)

_QUERY_QUERYTYPE = descriptor.EnumDescriptor(
  name='QueryType',
  full_name='Query.QueryType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='START', index=0, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='CONTINUE', index=1, number=2,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='STOP', index=2, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=245,
  serialized_end=291,
)

_FRAME_FRAMETYPE = descriptor.EnumDescriptor(
  name='FrameType',
  full_name='Frame.FrameType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='POS', index=0, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='OPT', index=1, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=360,
  serialized_end=389,
)

_RESPONSE_RESPONSETYPE = descriptor.EnumDescriptor(
  name='ResponseType',
  full_name='Response.ResponseType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='SUCCESS_ATOM', index=0, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='SUCCESS_SEQUENCE', index=1, number=2,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='SUCCESS_PARTIAL', index=2, number=3,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='CLIENT_ERROR', index=3, number=16,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='COMPILE_ERROR', index=4, number=17,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='RUNTIME_ERROR', index=5, number=18,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=552,
  serialized_end=683,
)

_DATUM_DATUMTYPE = descriptor.EnumDescriptor(
  name='DatumType',
  full_name='Datum.DatumType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='R_NULL', index=0, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='R_BOOL', index=1, number=2,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='R_NUM', index=2, number=3,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='R_STR', index=3, number=4,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='R_ARRAY', index=4, number=5,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='R_OBJECT', index=5, number=6,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=881,
  serialized_end=965,
)

_TERM_TERMTYPE = descriptor.EnumDescriptor(
  name='TermType',
  full_name='Term.TermType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='DATUM', index=0, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='MAKE_ARRAY', index=1, number=2,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='MAKE_OBJ', index=2, number=3,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='VAR', index=3, number=10,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='JAVASCRIPT', index=4, number=11,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='ERROR', index=5, number=12,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='IMPLICIT_VAR', index=6, number=13,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='DB', index=7, number=14,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='TABLE', index=8, number=15,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='GET', index=9, number=16,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='EQ', index=10, number=17,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='NE', index=11, number=18,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='LT', index=12, number=19,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='LE', index=13, number=20,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='GT', index=14, number=21,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='GE', index=15, number=22,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='NOT', index=16, number=23,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='ADD', index=17, number=24,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='SUB', index=18, number=25,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='MUL', index=19, number=26,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='DIV', index=20, number=27,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='MOD', index=21, number=28,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='APPEND', index=22, number=29,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='SLICE', index=23, number=30,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='SKIP', index=24, number=70,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='LIMIT', index=25, number=71,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='GETATTR', index=26, number=31,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='CONTAINS', index=27, number=32,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='PLUCK', index=28, number=33,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='WITHOUT', index=29, number=34,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='MERGE', index=30, number=35,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='BETWEEN', index=31, number=36,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='REDUCE', index=32, number=37,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='MAP', index=33, number=38,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='FILTER', index=34, number=39,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='CONCATMAP', index=35, number=40,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='ORDERBY', index=36, number=41,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='DISTINCT', index=37, number=42,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='COUNT', index=38, number=43,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='UNION', index=39, number=44,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='NTH', index=40, number=45,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='GROUPED_MAP_REDUCE', index=41, number=46,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='GROUPBY', index=42, number=47,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='INNER_JOIN', index=43, number=48,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='OUTER_JOIN', index=44, number=49,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='EQ_JOIN', index=45, number=50,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='ZIP', index=46, number=72,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='COERCE_TO', index=47, number=51,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='TYPEOF', index=48, number=52,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='UPDATE', index=49, number=53,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='DELETE', index=50, number=54,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='REPLACE', index=51, number=55,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='INSERT', index=52, number=56,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='DB_CREATE', index=53, number=57,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='DB_DROP', index=54, number=58,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='DB_LIST', index=55, number=59,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='TABLE_CREATE', index=56, number=60,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='TABLE_DROP', index=57, number=61,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='TABLE_LIST', index=58, number=62,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='FUNCALL', index=59, number=64,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='BRANCH', index=60, number=65,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='ANY', index=61, number=66,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='ALL', index=62, number=67,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='FOREACH', index=63, number=68,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='FUNC', index=64, number=69,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='ASC', index=65, number=73,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='DESC', index=66, number=74,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1140,
  serialized_end=1943,
)


_VERSIONDUMMY = descriptor.Descriptor(
  name='VersionDummy',
  full_name='VersionDummy',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _VERSIONDUMMY_VERSION,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=13,
  serialized_end=52,
)


_QUERY_ASSOCPAIR = descriptor.Descriptor(
  name='AssocPair',
  full_name='Query.AssocPair',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='key', full_name='Query.AssocPair.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='val', full_name='Query.AssocPair.val', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=199,
  serialized_end=243,
)

_QUERY = descriptor.Descriptor(
  name='Query',
  full_name='Query',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='type', full_name='Query.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='query', full_name='Query.query', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='token', full_name='Query.token', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='noreply', full_name='Query.noreply', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='global_optargs', full_name='Query.global_optargs', index=4,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_QUERY_ASSOCPAIR, ],
  enum_types=[
    _QUERY_QUERYTYPE,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=55,
  serialized_end=291,
)


_FRAME = descriptor.Descriptor(
  name='Frame',
  full_name='Frame',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='type', full_name='Frame.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='pos', full_name='Frame.pos', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='opt', full_name='Frame.opt', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _FRAME_FRAMETYPE,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=293,
  serialized_end=389,
)


_BACKTRACE = descriptor.Descriptor(
  name='Backtrace',
  full_name='Backtrace',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='frames', full_name='Backtrace.frames', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=391,
  serialized_end=426,
)


_RESPONSE = descriptor.Descriptor(
  name='Response',
  full_name='Response',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='type', full_name='Response.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='token', full_name='Response.token', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='response', full_name='Response.response', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='backtrace', full_name='Response.backtrace', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _RESPONSE_RESPONSETYPE,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=429,
  serialized_end=683,
)


_DATUM_ASSOCPAIR = descriptor.Descriptor(
  name='AssocPair',
  full_name='Datum.AssocPair',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='key', full_name='Datum.AssocPair.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='val', full_name='Datum.AssocPair.val', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=834,
  serialized_end=879,
)

_DATUM = descriptor.Descriptor(
  name='Datum',
  full_name='Datum',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='type', full_name='Datum.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='r_bool', full_name='Datum.r_bool', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='r_num', full_name='Datum.r_num', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='r_str', full_name='Datum.r_str', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='r_array', full_name='Datum.r_array', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='r_object', full_name='Datum.r_object', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_DATUM_ASSOCPAIR, ],
  enum_types=[
    _DATUM_DATUMTYPE,
  ],
  options=None,
  is_extendable=True,
  extension_ranges=[(10000, 20001), ],
  serialized_start=686,
  serialized_end=974,
)


_TERM_ASSOCPAIR = descriptor.Descriptor(
  name='AssocPair',
  full_name='Term.AssocPair',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='key', full_name='Term.AssocPair.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='val', full_name='Term.AssocPair.val', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=199,
  serialized_end=243,
)

_TERM = descriptor.Descriptor(
  name='Term',
  full_name='Term',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='type', full_name='Term.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='datum', full_name='Term.datum', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='args', full_name='Term.args', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='optargs', full_name='Term.optargs', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_TERM_ASSOCPAIR, ],
  enum_types=[
    _TERM_TERMTYPE,
  ],
  options=None,
  is_extendable=True,
  extension_ranges=[(10000, 20001), ],
  serialized_start=977,
  serialized_end=1952,
)

_VERSIONDUMMY_VERSION.containing_type = _VERSIONDUMMY;
_QUERY_ASSOCPAIR.fields_by_name['val'].message_type = _TERM
_QUERY_ASSOCPAIR.containing_type = _QUERY;
_QUERY.fields_by_name['type'].enum_type = _QUERY_QUERYTYPE
_QUERY.fields_by_name['query'].message_type = _TERM
_QUERY.fields_by_name['global_optargs'].message_type = _QUERY_ASSOCPAIR
_QUERY_QUERYTYPE.containing_type = _QUERY;
_FRAME.fields_by_name['type'].enum_type = _FRAME_FRAMETYPE
_FRAME_FRAMETYPE.containing_type = _FRAME;
_BACKTRACE.fields_by_name['frames'].message_type = _FRAME
_RESPONSE.fields_by_name['type'].enum_type = _RESPONSE_RESPONSETYPE
_RESPONSE.fields_by_name['response'].message_type = _DATUM
_RESPONSE.fields_by_name['backtrace'].message_type = _BACKTRACE
_RESPONSE_RESPONSETYPE.containing_type = _RESPONSE;
_DATUM_ASSOCPAIR.fields_by_name['val'].message_type = _DATUM
_DATUM_ASSOCPAIR.containing_type = _DATUM;
_DATUM.fields_by_name['type'].enum_type = _DATUM_DATUMTYPE
_DATUM.fields_by_name['r_array'].message_type = _DATUM
_DATUM.fields_by_name['r_object'].message_type = _DATUM_ASSOCPAIR
_DATUM_DATUMTYPE.containing_type = _DATUM;
_TERM_ASSOCPAIR.fields_by_name['val'].message_type = _TERM
_TERM_ASSOCPAIR.containing_type = _TERM;
_TERM.fields_by_name['type'].enum_type = _TERM_TERMTYPE
_TERM.fields_by_name['datum'].message_type = _DATUM
_TERM.fields_by_name['args'].message_type = _TERM
_TERM.fields_by_name['optargs'].message_type = _TERM_ASSOCPAIR
_TERM_TERMTYPE.containing_type = _TERM;
DESCRIPTOR.message_types_by_name['VersionDummy'] = _VERSIONDUMMY
DESCRIPTOR.message_types_by_name['Query'] = _QUERY
DESCRIPTOR.message_types_by_name['Frame'] = _FRAME
DESCRIPTOR.message_types_by_name['Backtrace'] = _BACKTRACE
DESCRIPTOR.message_types_by_name['Response'] = _RESPONSE
DESCRIPTOR.message_types_by_name['Datum'] = _DATUM
DESCRIPTOR.message_types_by_name['Term'] = _TERM

class VersionDummy(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _VERSIONDUMMY
  
  # @@protoc_insertion_point(class_scope:VersionDummy)

class Query(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  
  class AssocPair(message.Message):
    __metaclass__ = reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _QUERY_ASSOCPAIR
    
    # @@protoc_insertion_point(class_scope:Query.AssocPair)
  DESCRIPTOR = _QUERY
  
  # @@protoc_insertion_point(class_scope:Query)

class Frame(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _FRAME
  
  # @@protoc_insertion_point(class_scope:Frame)

class Backtrace(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _BACKTRACE
  
  # @@protoc_insertion_point(class_scope:Backtrace)

class Response(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _RESPONSE
  
  # @@protoc_insertion_point(class_scope:Response)

class Datum(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  
  class AssocPair(message.Message):
    __metaclass__ = reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _DATUM_ASSOCPAIR
    
    # @@protoc_insertion_point(class_scope:Datum.AssocPair)
  DESCRIPTOR = _DATUM
  
  # @@protoc_insertion_point(class_scope:Datum)

class Term(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  
  class AssocPair(message.Message):
    __metaclass__ = reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _TERM_ASSOCPAIR
    
    # @@protoc_insertion_point(class_scope:Term.AssocPair)
  DESCRIPTOR = _TERM
  
  # @@protoc_insertion_point(class_scope:Term)

# @@protoc_insertion_point(module_scope)
