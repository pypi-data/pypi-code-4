# -*- coding: ShiftJIS -*-
import re, bisect, unicodedata

UNKNOWN=0
ASCII=1
SJIS=2
EUC=3
JIS=4
UTF8=5
UTF16_LE=6
UTF16_BE=7

CONV_FAILED = b"\x22\x2e"

_tbl_jis2mskanji = {
b"\x22\x40" : b"\x87\x9c",
b"\x22\x41" : b"\x87\x9b",
b"\x22\x4c" : b"\xee\xf9",
b"\x22\x5c" : b"\x87\x97",
b"\x22\x5d" : b"\x87\x96",
b"\x22\x61" : b"\x87\x91",
b"\x22\x62" : b"\x87\x90",
b"\x22\x65" : b"\x87\x95",
b"\x22\x68" : b"\x87\x9a",
b"\x22\x69" : b"\x87\x92",
b"\x2d\x35" : b"\x87\x54",
b"\x2d\x36" : b"\x87\x55",
b"\x2d\x37" : b"\x87\x56",
b"\x2d\x38" : b"\x87\x57",
b"\x2d\x39" : b"\x87\x58",
b"\x2d\x3a" : b"\x87\x59",
b"\x2d\x3b" : b"\x87\x5a",
b"\x2d\x3c" : b"\x87\x5b",
b"\x2d\x3d" : b"\x87\x5c",
b"\x2d\x3e" : b"\x87\x5d",
b"\x2d\x62" : b"\x87\x82",
b"\x2d\x64" : b"\x87\x84",
b"\x2d\x6a" : b"\x87\x8a",
b"\x79\x21" : b"\xed\x40",
b"\x79\x22" : b"\xed\x41",
b"\x79\x23" : b"\xed\x42",
b"\x79\x24" : b"\xed\x43",
b"\x79\x25" : b"\xed\x44",
b"\x79\x26" : b"\xed\x45",
b"\x79\x27" : b"\xed\x46",
b"\x79\x28" : b"\xed\x47",
b"\x79\x29" : b"\xed\x48",
b"\x79\x2a" : b"\xed\x49",
b"\x79\x2b" : b"\xed\x4a",
b"\x79\x2c" : b"\xed\x4b",
b"\x79\x2d" : b"\xed\x4c",
b"\x79\x2e" : b"\xed\x4d",
b"\x79\x2f" : b"\xed\x4e",
b"\x79\x30" : b"\xed\x4f",
b"\x79\x31" : b"\xed\x50",
b"\x79\x32" : b"\xed\x51",
b"\x79\x33" : b"\xed\x52",
b"\x79\x34" : b"\xed\x53",
b"\x79\x35" : b"\xed\x54",
b"\x79\x36" : b"\xed\x55",
b"\x79\x37" : b"\xed\x56",
b"\x79\x38" : b"\xed\x57",
b"\x79\x39" : b"\xed\x58",
b"\x79\x3a" : b"\xed\x59",
b"\x79\x3b" : b"\xed\x5a",
b"\x79\x3c" : b"\xed\x5b",
b"\x79\x3d" : b"\xed\x5c",
b"\x79\x3e" : b"\xed\x5d",
b"\x79\x3f" : b"\xed\x5e",
b"\x79\x40" : b"\xed\x5f",
b"\x79\x41" : b"\xed\x60",
b"\x79\x42" : b"\xed\x61",
b"\x79\x43" : b"\xed\x62",
b"\x79\x44" : b"\xed\x63",
b"\x79\x45" : b"\xed\x64",
b"\x79\x46" : b"\xed\x65",
b"\x79\x47" : b"\xed\x66",
b"\x79\x48" : b"\xed\x67",
b"\x79\x49" : b"\xed\x68",
b"\x79\x4a" : b"\xed\x69",
b"\x79\x4b" : b"\xed\x6a",
b"\x79\x4c" : b"\xed\x6b",
b"\x79\x4d" : b"\xed\x6c",
b"\x79\x4e" : b"\xed\x6d",
b"\x79\x4f" : b"\xed\x6e",
b"\x79\x50" : b"\xed\x6f",
b"\x79\x51" : b"\xed\x70",
b"\x79\x52" : b"\xed\x71",
b"\x79\x53" : b"\xed\x72",
b"\x79\x54" : b"\xed\x73",
b"\x79\x55" : b"\xed\x74",
b"\x79\x56" : b"\xed\x75",
b"\x79\x57" : b"\xed\x76",
b"\x79\x58" : b"\xed\x77",
b"\x79\x59" : b"\xed\x78",
b"\x79\x5a" : b"\xed\x79",
b"\x79\x5b" : b"\xed\x7a",
b"\x79\x5c" : b"\xed\x7b",
b"\x79\x5d" : b"\xed\x7c",
b"\x79\x5e" : b"\xed\x7d",
b"\x79\x5f" : b"\xed\x7e",
b"\x79\x60" : b"\xed\x80",
b"\x79\x61" : b"\xed\x81",
b"\x79\x62" : b"\xed\x82",
b"\x79\x63" : b"\xed\x83",
b"\x79\x64" : b"\xed\x84",
b"\x79\x65" : b"\xed\x85",
b"\x79\x66" : b"\xed\x86",
b"\x79\x67" : b"\xed\x87",
b"\x79\x68" : b"\xed\x88",
b"\x79\x69" : b"\xed\x89",
b"\x79\x6a" : b"\xed\x8a",
b"\x79\x6b" : b"\xed\x8b",
b"\x79\x6c" : b"\xed\x8c",
b"\x79\x6d" : b"\xed\x8d",
b"\x79\x6e" : b"\xed\x8e",
b"\x79\x6f" : b"\xed\x8f",
b"\x79\x70" : b"\xed\x90",
b"\x79\x71" : b"\xed\x91",
b"\x79\x72" : b"\xed\x92",
b"\x79\x73" : b"\xed\x93",
b"\x79\x74" : b"\xed\x94",
b"\x79\x75" : b"\xed\x95",
b"\x79\x76" : b"\xed\x96",
b"\x79\x77" : b"\xed\x97",
b"\x79\x78" : b"\xed\x98",
b"\x79\x79" : b"\xed\x99",
b"\x79\x7a" : b"\xed\x9a",
b"\x79\x7b" : b"\xed\x9b",
b"\x79\x7c" : b"\xed\x9c",
b"\x79\x7d" : b"\xed\x9d",
b"\x79\x7e" : b"\xed\x9e",
b"\x7a\x21" : b"\xed\x9f",
b"\x7a\x22" : b"\xed\xa0",
b"\x7a\x23" : b"\xed\xa1",
b"\x7a\x24" : b"\xed\xa2",
b"\x7a\x25" : b"\xed\xa3",
b"\x7a\x26" : b"\xed\xa4",
b"\x7a\x27" : b"\xed\xa5",
b"\x7a\x28" : b"\xed\xa6",
b"\x7a\x29" : b"\xed\xa7",
b"\x7a\x2a" : b"\xed\xa8",
b"\x7a\x2b" : b"\xed\xa9",
b"\x7a\x2c" : b"\xed\xaa",
b"\x7a\x2d" : b"\xed\xab",
b"\x7a\x2e" : b"\xed\xac",
b"\x7a\x2f" : b"\xed\xad",
b"\x7a\x30" : b"\xed\xae",
b"\x7a\x31" : b"\xed\xaf",
b"\x7a\x32" : b"\xed\xb0",
b"\x7a\x33" : b"\xed\xb1",
b"\x7a\x34" : b"\xed\xb2",
b"\x7a\x35" : b"\xed\xb3",
b"\x7a\x36" : b"\xed\xb4",
b"\x7a\x37" : b"\xed\xb5",
b"\x7a\x38" : b"\xed\xb6",
b"\x7a\x39" : b"\xed\xb7",
b"\x7a\x3a" : b"\xed\xb8",
b"\x7a\x3b" : b"\xed\xb9",
b"\x7a\x3c" : b"\xed\xba",
b"\x7a\x3d" : b"\xed\xbb",
b"\x7a\x3e" : b"\xed\xbc",
b"\x7a\x3f" : b"\xed\xbd",
b"\x7a\x40" : b"\xed\xbe",
b"\x7a\x41" : b"\xed\xbf",
b"\x7a\x42" : b"\xed\xc0",
b"\x7a\x43" : b"\xed\xc1",
b"\x7a\x44" : b"\xed\xc2",
b"\x7a\x45" : b"\xed\xc3",
b"\x7a\x46" : b"\xed\xc4",
b"\x7a\x47" : b"\xed\xc5",
b"\x7a\x48" : b"\xed\xc6",
b"\x7a\x49" : b"\xed\xc7",
b"\x7a\x4a" : b"\xed\xc8",
b"\x7a\x4b" : b"\xed\xc9",
b"\x7a\x4c" : b"\xed\xca",
b"\x7a\x4d" : b"\xed\xcb",
b"\x7a\x4e" : b"\xed\xcc",
b"\x7a\x4f" : b"\xed\xcd",
b"\x7a\x50" : b"\xed\xce",
b"\x7a\x51" : b"\xed\xcf",
b"\x7a\x52" : b"\xed\xd0",
b"\x7a\x53" : b"\xed\xd1",
b"\x7a\x54" : b"\xed\xd2",
b"\x7a\x55" : b"\xed\xd3",
b"\x7a\x56" : b"\xed\xd4",
b"\x7a\x57" : b"\xed\xd5",
b"\x7a\x58" : b"\xed\xd6",
b"\x7a\x59" : b"\xed\xd7",
b"\x7a\x5a" : b"\xed\xd8",
b"\x7a\x5b" : b"\xed\xd9",
b"\x7a\x5c" : b"\xed\xda",
b"\x7a\x5d" : b"\xed\xdb",
b"\x7a\x5e" : b"\xed\xdc",
b"\x7a\x5f" : b"\xed\xdd",
b"\x7a\x60" : b"\xed\xde",
b"\x7a\x61" : b"\xed\xdf",
b"\x7a\x62" : b"\xed\xe0",
b"\x7a\x63" : b"\xed\xe1",
b"\x7a\x64" : b"\xed\xe2",
b"\x7a\x65" : b"\xed\xe3",
b"\x7a\x66" : b"\xed\xe4",
b"\x7a\x67" : b"\xed\xe5",
b"\x7a\x68" : b"\xed\xe6",
b"\x7a\x69" : b"\xed\xe7",
b"\x7a\x6a" : b"\xed\xe8",
b"\x7a\x6b" : b"\xed\xe9",
b"\x7a\x6c" : b"\xed\xea",
b"\x7a\x6d" : b"\xed\xeb",
b"\x7a\x6e" : b"\xed\xec",
b"\x7a\x6f" : b"\xed\xed",
b"\x7a\x70" : b"\xed\xee",
b"\x7a\x71" : b"\xed\xef",
b"\x7a\x72" : b"\xed\xf0",
b"\x7a\x73" : b"\xed\xf1",
b"\x7a\x74" : b"\xed\xf2",
b"\x7a\x75" : b"\xed\xf3",
b"\x7a\x76" : b"\xed\xf4",
b"\x7a\x77" : b"\xed\xf5",
b"\x7a\x78" : b"\xed\xf6",
b"\x7a\x79" : b"\xed\xf7",
b"\x7a\x7a" : b"\xed\xf8",
b"\x7a\x7b" : b"\xed\xf9",
b"\x7a\x7c" : b"\xed\xfa",
b"\x7a\x7d" : b"\xed\xfb",
b"\x7a\x7e" : b"\xed\xfc",
b"\x7b\x21" : b"\xee\x40",
b"\x7b\x22" : b"\xee\x41",
b"\x7b\x23" : b"\xee\x42",
b"\x7b\x24" : b"\xee\x43",
b"\x7b\x25" : b"\xee\x44",
b"\x7b\x26" : b"\xee\x45",
b"\x7b\x27" : b"\xee\x46",
b"\x7b\x28" : b"\xee\x47",
b"\x7b\x29" : b"\xee\x48",
b"\x7b\x2a" : b"\xee\x49",
b"\x7b\x2b" : b"\xee\x4a",
b"\x7b\x2c" : b"\xee\x4b",
b"\x7b\x2d" : b"\xee\x4c",
b"\x7b\x2e" : b"\xee\x4d",
b"\x7b\x2f" : b"\xee\x4e",
b"\x7b\x30" : b"\xee\x4f",
b"\x7b\x31" : b"\xee\x50",
b"\x7b\x32" : b"\xee\x51",
b"\x7b\x33" : b"\xee\x52",
b"\x7b\x34" : b"\xee\x53",
b"\x7b\x35" : b"\xee\x54",
b"\x7b\x36" : b"\xee\x55",
b"\x7b\x37" : b"\xee\x56",
b"\x7b\x38" : b"\xee\x57",
b"\x7b\x39" : b"\xee\x58",
b"\x7b\x3a" : b"\xee\x59",
b"\x7b\x3b" : b"\xee\x5a",
b"\x7b\x3c" : b"\xee\x5b",
b"\x7b\x3d" : b"\xee\x5c",
b"\x7b\x3e" : b"\xee\x5d",
b"\x7b\x3f" : b"\xee\x5e",
b"\x7b\x40" : b"\xee\x5f",
b"\x7b\x41" : b"\xee\x60",
b"\x7b\x42" : b"\xee\x61",
b"\x7b\x43" : b"\xee\x62",
b"\x7b\x44" : b"\xee\x63",
b"\x7b\x45" : b"\xee\x64",
b"\x7b\x46" : b"\xee\x65",
b"\x7b\x47" : b"\xee\x66",
b"\x7b\x48" : b"\xee\x67",
b"\x7b\x49" : b"\xee\x68",
b"\x7b\x4a" : b"\xee\x69",
b"\x7b\x4b" : b"\xee\x6a",
b"\x7b\x4c" : b"\xee\x6b",
b"\x7b\x4d" : b"\xee\x6c",
b"\x7b\x4e" : b"\xee\x6d",
b"\x7b\x4f" : b"\xee\x6e",
b"\x7b\x50" : b"\xee\x6f",
b"\x7b\x51" : b"\xee\x70",
b"\x7b\x52" : b"\xee\x71",
b"\x7b\x53" : b"\xee\x72",
b"\x7b\x54" : b"\xee\x73",
b"\x7b\x55" : b"\xee\x74",
b"\x7b\x56" : b"\xee\x75",
b"\x7b\x57" : b"\xee\x76",
b"\x7b\x58" : b"\xee\x77",
b"\x7b\x59" : b"\xee\x78",
b"\x7b\x5a" : b"\xee\x79",
b"\x7b\x5b" : b"\xee\x7a",
b"\x7b\x5c" : b"\xee\x7b",
b"\x7b\x5d" : b"\xee\x7c",
b"\x7b\x5e" : b"\xee\x7d",
b"\x7b\x5f" : b"\xee\x7e",
b"\x7b\x60" : b"\xee\x80",
b"\x7b\x61" : b"\xee\x81",
b"\x7b\x62" : b"\xee\x82",
b"\x7b\x63" : b"\xee\x83",
b"\x7b\x64" : b"\xee\x84",
b"\x7b\x65" : b"\xee\x85",
b"\x7b\x66" : b"\xee\x86",
b"\x7b\x67" : b"\xee\x87",
b"\x7b\x68" : b"\xee\x88",
b"\x7b\x69" : b"\xee\x89",
b"\x7b\x6a" : b"\xee\x8a",
b"\x7b\x6b" : b"\xee\x8b",
b"\x7b\x6c" : b"\xee\x8c",
b"\x7b\x6d" : b"\xee\x8d",
b"\x7b\x6e" : b"\xee\x8e",
b"\x7b\x6f" : b"\xee\x8f",
b"\x7b\x70" : b"\xee\x90",
b"\x7b\x71" : b"\xee\x91",
b"\x7b\x72" : b"\xee\x92",
b"\x7b\x73" : b"\xee\x93",
b"\x7b\x74" : b"\xee\x94",
b"\x7b\x75" : b"\xee\x95",
b"\x7b\x76" : b"\xee\x96",
b"\x7b\x77" : b"\xee\x97",
b"\x7b\x78" : b"\xee\x98",
b"\x7b\x79" : b"\xee\x99",
b"\x7b\x7a" : b"\xee\x9a",
b"\x7b\x7b" : b"\xee\x9b",
b"\x7b\x7c" : b"\xee\x9c",
b"\x7b\x7d" : b"\xee\x9d",
b"\x7b\x7e" : b"\xee\x9e",
b"\x7c\x21" : b"\xee\x9f",
b"\x7c\x22" : b"\xee\xa0",
b"\x7c\x23" : b"\xee\xa1",
b"\x7c\x24" : b"\xee\xa2",
b"\x7c\x25" : b"\xee\xa3",
b"\x7c\x26" : b"\xee\xa4",
b"\x7c\x27" : b"\xee\xa5",
b"\x7c\x28" : b"\xee\xa6",
b"\x7c\x29" : b"\xee\xa7",
b"\x7c\x2a" : b"\xee\xa8",
b"\x7c\x2b" : b"\xee\xa9",
b"\x7c\x2c" : b"\xee\xaa",
b"\x7c\x2d" : b"\xee\xab",
b"\x7c\x2e" : b"\xee\xac",
b"\x7c\x2f" : b"\xee\xad",
b"\x7c\x30" : b"\xee\xae",
b"\x7c\x31" : b"\xee\xaf",
b"\x7c\x32" : b"\xee\xb0",
b"\x7c\x33" : b"\xee\xb1",
b"\x7c\x34" : b"\xee\xb2",
b"\x7c\x35" : b"\xee\xb3",
b"\x7c\x36" : b"\xee\xb4",
b"\x7c\x37" : b"\xee\xb5",
b"\x7c\x38" : b"\xee\xb6",
b"\x7c\x39" : b"\xee\xb7",
b"\x7c\x3a" : b"\xee\xb8",
b"\x7c\x3b" : b"\xee\xb9",
b"\x7c\x3c" : b"\xee\xba",
b"\x7c\x3d" : b"\xee\xbb",
b"\x7c\x3e" : b"\xee\xbc",
b"\x7c\x3f" : b"\xee\xbd",
b"\x7c\x40" : b"\xee\xbe",
b"\x7c\x41" : b"\xee\xbf",
b"\x7c\x42" : b"\xee\xc0",
b"\x7c\x43" : b"\xee\xc1",
b"\x7c\x44" : b"\xee\xc2",
b"\x7c\x45" : b"\xee\xc3",
b"\x7c\x46" : b"\xee\xc4",
b"\x7c\x47" : b"\xee\xc5",
b"\x7c\x48" : b"\xee\xc6",
b"\x7c\x49" : b"\xee\xc7",
b"\x7c\x4a" : b"\xee\xc8",
b"\x7c\x4b" : b"\xee\xc9",
b"\x7c\x4c" : b"\xee\xca",
b"\x7c\x4d" : b"\xee\xcb",
b"\x7c\x4e" : b"\xee\xcc",
b"\x7c\x4f" : b"\xee\xcd",
b"\x7c\x50" : b"\xee\xce",
b"\x7c\x51" : b"\xee\xcf",
b"\x7c\x52" : b"\xee\xd0",
b"\x7c\x53" : b"\xee\xd1",
b"\x7c\x54" : b"\xee\xd2",
b"\x7c\x55" : b"\xee\xd3",
b"\x7c\x56" : b"\xee\xd4",
b"\x7c\x57" : b"\xee\xd5",
b"\x7c\x58" : b"\xee\xd6",
b"\x7c\x59" : b"\xee\xd7",
b"\x7c\x5a" : b"\xee\xd8",
b"\x7c\x5b" : b"\xee\xd9",
b"\x7c\x5c" : b"\xee\xda",
b"\x7c\x5d" : b"\xee\xdb",
b"\x7c\x5e" : b"\xee\xdc",
b"\x7c\x5f" : b"\xee\xdd",
b"\x7c\x60" : b"\xee\xde",
b"\x7c\x61" : b"\xee\xdf",
b"\x7c\x62" : b"\xee\xe0",
b"\x7c\x63" : b"\xee\xe1",
b"\x7c\x64" : b"\xee\xe2",
b"\x7c\x65" : b"\xee\xe3",
b"\x7c\x66" : b"\xee\xe4",
b"\x7c\x67" : b"\xee\xe5",
b"\x7c\x68" : b"\xee\xe6",
b"\x7c\x69" : b"\xee\xe7",
b"\x7c\x6a" : b"\xee\xe8",
b"\x7c\x6b" : b"\xee\xe9",
b"\x7c\x6c" : b"\xee\xea",
b"\x7c\x6d" : b"\xee\xeb",
b"\x7c\x6e" : b"\xee\xec",
b"\x7c\x71" : b"\xee\xef",
b"\x7c\x72" : b"\xee\xf0",
b"\x7c\x73" : b"\xee\xf1",
b"\x7c\x74" : b"\xee\xf2",
b"\x7c\x75" : b"\xee\xf3",
b"\x7c\x76" : b"\xee\xf4",
b"\x7c\x77" : b"\xee\xf5",
b"\x7c\x78" : b"\xee\xf6",
b"\x7c\x79" : b"\xee\xf7",
b"\x7c\x7a" : b"\xee\xf8",
b"\x7c\x7c" : b"\xee\xfa",
b"\x7c\x7d" : b"\xee\xfb",
b"\x7c\x7e" : b"\xee\xfc", }


_tbl_mskanji2jis = {
b"\x87\x90" : b"\x22\x62",
b"\x87\x91" : b"\x22\x61",
b"\x87\x92" : b"\x22\x69",
b"\x87\x95" : b"\x22\x65",
b"\x87\x96" : b"\x22\x5d",
b"\x87\x97" : b"\x22\x5c",
b"\x87\x9a" : b"\x22\x68",
b"\x87\x9b" : b"\x22\x41",
b"\x87\x9c" : b"\x22\x40",
b"\xee\xf9" : b"\x22\x4c",
b"\xfa\x40" : b"\x7c\x71",
b"\xfa\x41" : b"\x7c\x72",
b"\xfa\x42" : b"\x7c\x73",
b"\xfa\x43" : b"\x7c\x74",
b"\xfa\x44" : b"\x7c\x75",
b"\xfa\x45" : b"\x7c\x76",
b"\xfa\x46" : b"\x7c\x77",
b"\xfa\x47" : b"\x7c\x78",
b"\xfa\x48" : b"\x7c\x79",
b"\xfa\x49" : b"\x7c\x7a",
b"\xfa\x4a" : b"\x2d\x35",
b"\xfa\x4b" : b"\x2d\x36",
b"\xfa\x4c" : b"\x2d\x37",
b"\xfa\x4d" : b"\x2d\x38",
b"\xfa\x4e" : b"\x2d\x39",
b"\xfa\x4f" : b"\x2d\x3a",
b"\xfa\x50" : b"\x2d\x3b",
b"\xfa\x51" : b"\x2d\x3c",
b"\xfa\x52" : b"\x2d\x3d",
b"\xfa\x53" : b"\x2d\x3e",
b"\xfa\x54" : b"\x22\x4c",
b"\xfa\x55" : b"\x7c\x7c",
b"\xfa\x56" : b"\x7c\x7d",
b"\xfa\x57" : b"\x7c\x7e",
b"\xfa\x58" : b"\x2d\x6a",
b"\xfa\x59" : b"\x2d\x62",
b"\xfa\x5a" : b"\x2d\x64",
b"\xfa\x5b" : b"\x22\x68",
b"\xfa\x5c" : b"\x79\x21",
b"\xfa\x5d" : b"\x79\x22",
b"\xfa\x5e" : b"\x79\x23",
b"\xfa\x5f" : b"\x79\x24",
b"\xfa\x60" : b"\x79\x25",
b"\xfa\x61" : b"\x79\x26",
b"\xfa\x62" : b"\x79\x27",
b"\xfa\x63" : b"\x79\x28",
b"\xfa\x64" : b"\x79\x29",
b"\xfa\x65" : b"\x79\x2a",
b"\xfa\x66" : b"\x79\x2b",
b"\xfa\x67" : b"\x79\x2c",
b"\xfa\x68" : b"\x79\x2d",
b"\xfa\x69" : b"\x79\x2e",
b"\xfa\x6a" : b"\x79\x2f",
b"\xfa\x6b" : b"\x79\x30",
b"\xfa\x6c" : b"\x79\x31",
b"\xfa\x6d" : b"\x79\x32",
b"\xfa\x6e" : b"\x79\x33",
b"\xfa\x6f" : b"\x79\x34",
b"\xfa\x70" : b"\x79\x35",
b"\xfa\x71" : b"\x79\x36",
b"\xfa\x72" : b"\x79\x37",
b"\xfa\x73" : b"\x79\x38",
b"\xfa\x74" : b"\x79\x39",
b"\xfa\x75" : b"\x79\x3a",
b"\xfa\x76" : b"\x79\x3b",
b"\xfa\x77" : b"\x79\x3c",
b"\xfa\x78" : b"\x79\x3d",
b"\xfa\x79" : b"\x79\x3e",
b"\xfa\x7a" : b"\x79\x3f",
b"\xfa\x7b" : b"\x79\x40",
b"\xfa\x7c" : b"\x79\x41",
b"\xfa\x7d" : b"\x79\x42",
b"\xfa\x7e" : b"\x79\x43",
b"\xfa\x80" : b"\x79\x44",
b"\xfa\x81" : b"\x79\x45",
b"\xfa\x82" : b"\x79\x46",
b"\xfa\x83" : b"\x79\x47",
b"\xfa\x84" : b"\x79\x48",
b"\xfa\x85" : b"\x79\x49",
b"\xfa\x86" : b"\x79\x4a",
b"\xfa\x87" : b"\x79\x4b",
b"\xfa\x88" : b"\x79\x4c",
b"\xfa\x89" : b"\x79\x4d",
b"\xfa\x8a" : b"\x79\x4e",
b"\xfa\x8b" : b"\x79\x4f",
b"\xfa\x8c" : b"\x79\x50",
b"\xfa\x8d" : b"\x79\x51",
b"\xfa\x8e" : b"\x79\x52",
b"\xfa\x8f" : b"\x79\x53",
b"\xfa\x90" : b"\x79\x54",
b"\xfa\x91" : b"\x79\x55",
b"\xfa\x92" : b"\x79\x56",
b"\xfa\x93" : b"\x79\x57",
b"\xfa\x94" : b"\x79\x58",
b"\xfa\x95" : b"\x79\x59",
b"\xfa\x96" : b"\x79\x5a",
b"\xfa\x97" : b"\x79\x5b",
b"\xfa\x98" : b"\x79\x5c",
b"\xfa\x99" : b"\x79\x5d",
b"\xfa\x9a" : b"\x79\x5e",
b"\xfa\x9b" : b"\x79\x5f",
b"\xfa\x9c" : b"\x79\x60",
b"\xfa\x9d" : b"\x79\x61",
b"\xfa\x9e" : b"\x79\x62",
b"\xfa\x9f" : b"\x79\x63",
b"\xfa\xa0" : b"\x79\x64",
b"\xfa\xa1" : b"\x79\x65",
b"\xfa\xa2" : b"\x79\x66",
b"\xfa\xa3" : b"\x79\x67",
b"\xfa\xa4" : b"\x79\x68",
b"\xfa\xa5" : b"\x79\x69",
b"\xfa\xa6" : b"\x79\x6a",
b"\xfa\xa7" : b"\x79\x6b",
b"\xfa\xa8" : b"\x79\x6c",
b"\xfa\xa9" : b"\x79\x6d",
b"\xfa\xaa" : b"\x79\x6e",
b"\xfa\xab" : b"\x79\x6f",
b"\xfa\xac" : b"\x79\x70",
b"\xfa\xad" : b"\x79\x71",
b"\xfa\xae" : b"\x79\x72",
b"\xfa\xaf" : b"\x79\x73",
b"\xfa\xb0" : b"\x79\x74",
b"\xfa\xb1" : b"\x79\x75",
b"\xfa\xb2" : b"\x79\x76",
b"\xfa\xb3" : b"\x79\x77",
b"\xfa\xb4" : b"\x79\x78",
b"\xfa\xb5" : b"\x79\x79",
b"\xfa\xb6" : b"\x79\x7a",
b"\xfa\xb7" : b"\x79\x7b",
b"\xfa\xb8" : b"\x79\x7c",
b"\xfa\xb9" : b"\x79\x7d",
b"\xfa\xba" : b"\x79\x7e",
b"\xfa\xbb" : b"\x7a\x21",
b"\xfa\xbc" : b"\x7a\x22",
b"\xfa\xbd" : b"\x7a\x23",
b"\xfa\xbe" : b"\x7a\x24",
b"\xfa\xbf" : b"\x7a\x25",
b"\xfa\xc0" : b"\x7a\x26",
b"\xfa\xc1" : b"\x7a\x27",
b"\xfa\xc2" : b"\x7a\x28",
b"\xfa\xc3" : b"\x7a\x29",
b"\xfa\xc4" : b"\x7a\x2a",
b"\xfa\xc5" : b"\x7a\x2b",
b"\xfa\xc6" : b"\x7a\x2c",
b"\xfa\xc7" : b"\x7a\x2d",
b"\xfa\xc8" : b"\x7a\x2e",
b"\xfa\xc9" : b"\x7a\x2f",
b"\xfa\xca" : b"\x7a\x30",
b"\xfa\xcb" : b"\x7a\x31",
b"\xfa\xcc" : b"\x7a\x32",
b"\xfa\xcd" : b"\x7a\x33",
b"\xfa\xce" : b"\x7a\x34",
b"\xfa\xcf" : b"\x7a\x35",
b"\xfa\xd0" : b"\x7a\x36",
b"\xfa\xd1" : b"\x7a\x37",
b"\xfa\xd2" : b"\x7a\x38",
b"\xfa\xd3" : b"\x7a\x39",
b"\xfa\xd4" : b"\x7a\x3a",
b"\xfa\xd5" : b"\x7a\x3b",
b"\xfa\xd6" : b"\x7a\x3c",
b"\xfa\xd7" : b"\x7a\x3d",
b"\xfa\xd8" : b"\x7a\x3e",
b"\xfa\xd9" : b"\x7a\x3f",
b"\xfa\xda" : b"\x7a\x40",
b"\xfa\xdb" : b"\x7a\x41",
b"\xfa\xdc" : b"\x7a\x42",
b"\xfa\xdd" : b"\x7a\x43",
b"\xfa\xde" : b"\x7a\x44",
b"\xfa\xdf" : b"\x7a\x45",
b"\xfa\xe0" : b"\x7a\x46",
b"\xfa\xe1" : b"\x7a\x47",
b"\xfa\xe2" : b"\x7a\x48",
b"\xfa\xe3" : b"\x7a\x49",
b"\xfa\xe4" : b"\x7a\x4a",
b"\xfa\xe5" : b"\x7a\x4b",
b"\xfa\xe6" : b"\x7a\x4c",
b"\xfa\xe7" : b"\x7a\x4d",
b"\xfa\xe8" : b"\x7a\x4e",
b"\xfa\xe9" : b"\x7a\x4f",
b"\xfa\xea" : b"\x7a\x50",
b"\xfa\xeb" : b"\x7a\x51",
b"\xfa\xec" : b"\x7a\x52",
b"\xfa\xed" : b"\x7a\x53",
b"\xfa\xee" : b"\x7a\x54",
b"\xfa\xef" : b"\x7a\x55",
b"\xfa\xf0" : b"\x7a\x56",
b"\xfa\xf1" : b"\x7a\x57",
b"\xfa\xf2" : b"\x7a\x58",
b"\xfa\xf3" : b"\x7a\x59",
b"\xfa\xf4" : b"\x7a\x5a",
b"\xfa\xf5" : b"\x7a\x5b",
b"\xfa\xf6" : b"\x7a\x5c",
b"\xfa\xf7" : b"\x7a\x5d",
b"\xfa\xf8" : b"\x7a\x5e",
b"\xfa\xf9" : b"\x7a\x5f",
b"\xfa\xfa" : b"\x7a\x60",
b"\xfa\xfb" : b"\x7a\x61",
b"\xfa\xfc" : b"\x7a\x62",
b"\xfb\x40" : b"\x7a\x63",
b"\xfb\x41" : b"\x7a\x64",
b"\xfb\x42" : b"\x7a\x65",
b"\xfb\x43" : b"\x7a\x66",
b"\xfb\x44" : b"\x7a\x67",
b"\xfb\x45" : b"\x7a\x68",
b"\xfb\x46" : b"\x7a\x69",
b"\xfb\x47" : b"\x7a\x6a",
b"\xfb\x48" : b"\x7a\x6b",
b"\xfb\x49" : b"\x7a\x6c",
b"\xfb\x4a" : b"\x7a\x6d",
b"\xfb\x4b" : b"\x7a\x6e",
b"\xfb\x4c" : b"\x7a\x6f",
b"\xfb\x4d" : b"\x7a\x70",
b"\xfb\x4e" : b"\x7a\x71",
b"\xfb\x4f" : b"\x7a\x72",
b"\xfb\x50" : b"\x7a\x73",
b"\xfb\x51" : b"\x7a\x74",
b"\xfb\x52" : b"\x7a\x75",
b"\xfb\x53" : b"\x7a\x76",
b"\xfb\x54" : b"\x7a\x77",
b"\xfb\x55" : b"\x7a\x78",
b"\xfb\x56" : b"\x7a\x79",
b"\xfb\x57" : b"\x7a\x7a",
b"\xfb\x58" : b"\x7a\x7b",
b"\xfb\x59" : b"\x7a\x7c",
b"\xfb\x5a" : b"\x7a\x7d",
b"\xfb\x5b" : b"\x7a\x7e",
b"\xfb\x5c" : b"\x7b\x21",
b"\xfb\x5d" : b"\x7b\x22",
b"\xfb\x5e" : b"\x7b\x23",
b"\xfb\x5f" : b"\x7b\x24",
b"\xfb\x60" : b"\x7b\x25",
b"\xfb\x61" : b"\x7b\x26",
b"\xfb\x62" : b"\x7b\x27",
b"\xfb\x63" : b"\x7b\x28",
b"\xfb\x64" : b"\x7b\x29",
b"\xfb\x65" : b"\x7b\x2a",
b"\xfb\x66" : b"\x7b\x2b",
b"\xfb\x67" : b"\x7b\x2c",
b"\xfb\x68" : b"\x7b\x2d",
b"\xfb\x69" : b"\x7b\x2e",
b"\xfb\x6a" : b"\x7b\x2f",
b"\xfb\x6b" : b"\x7b\x30",
b"\xfb\x6c" : b"\x7b\x31",
b"\xfb\x6d" : b"\x7b\x32",
b"\xfb\x6e" : b"\x7b\x33",
b"\xfb\x6f" : b"\x7b\x34",
b"\xfb\x70" : b"\x7b\x35",
b"\xfb\x71" : b"\x7b\x36",
b"\xfb\x72" : b"\x7b\x37",
b"\xfb\x73" : b"\x7b\x38",
b"\xfb\x74" : b"\x7b\x39",
b"\xfb\x75" : b"\x7b\x3a",
b"\xfb\x76" : b"\x7b\x3b",
b"\xfb\x77" : b"\x7b\x3c",
b"\xfb\x78" : b"\x7b\x3d",
b"\xfb\x79" : b"\x7b\x3e",
b"\xfb\x7a" : b"\x7b\x3f",
b"\xfb\x7b" : b"\x7b\x40",
b"\xfb\x7c" : b"\x7b\x41",
b"\xfb\x7d" : b"\x7b\x42",
b"\xfb\x7e" : b"\x7b\x43",
b"\xfb\x80" : b"\x7b\x44",
b"\xfb\x81" : b"\x7b\x45",
b"\xfb\x82" : b"\x7b\x46",
b"\xfb\x83" : b"\x7b\x47",
b"\xfb\x84" : b"\x7b\x48",
b"\xfb\x85" : b"\x7b\x49",
b"\xfb\x86" : b"\x7b\x4a",
b"\xfb\x87" : b"\x7b\x4b",
b"\xfb\x88" : b"\x7b\x4c",
b"\xfb\x89" : b"\x7b\x4d",
b"\xfb\x8a" : b"\x7b\x4e",
b"\xfb\x8b" : b"\x7b\x4f",
b"\xfb\x8c" : b"\x7b\x50",
b"\xfb\x8d" : b"\x7b\x51",
b"\xfb\x8e" : b"\x7b\x52",
b"\xfb\x8f" : b"\x7b\x53",
b"\xfb\x90" : b"\x7b\x54",
b"\xfb\x91" : b"\x7b\x55",
b"\xfb\x92" : b"\x7b\x56",
b"\xfb\x93" : b"\x7b\x57",
b"\xfb\x94" : b"\x7b\x58",
b"\xfb\x95" : b"\x7b\x59",
b"\xfb\x96" : b"\x7b\x5a",
b"\xfb\x97" : b"\x7b\x5b",
b"\xfb\x98" : b"\x7b\x5c",
b"\xfb\x99" : b"\x7b\x5d",
b"\xfb\x9a" : b"\x7b\x5e",
b"\xfb\x9b" : b"\x7b\x5f",
b"\xfb\x9c" : b"\x7b\x60",
b"\xfb\x9d" : b"\x7b\x61",
b"\xfb\x9e" : b"\x7b\x62",
b"\xfb\x9f" : b"\x7b\x63",
b"\xfb\xa0" : b"\x7b\x64",
b"\xfb\xa1" : b"\x7b\x65",
b"\xfb\xa2" : b"\x7b\x66",
b"\xfb\xa3" : b"\x7b\x67",
b"\xfb\xa4" : b"\x7b\x68",
b"\xfb\xa5" : b"\x7b\x69",
b"\xfb\xa6" : b"\x7b\x6a",
b"\xfb\xa7" : b"\x7b\x6b",
b"\xfb\xa8" : b"\x7b\x6c",
b"\xfb\xa9" : b"\x7b\x6d",
b"\xfb\xaa" : b"\x7b\x6e",
b"\xfb\xab" : b"\x7b\x6f",
b"\xfb\xac" : b"\x7b\x70",
b"\xfb\xad" : b"\x7b\x71",
b"\xfb\xae" : b"\x7b\x72",
b"\xfb\xaf" : b"\x7b\x73",
b"\xfb\xb0" : b"\x7b\x74",
b"\xfb\xb1" : b"\x7b\x75",
b"\xfb\xb2" : b"\x7b\x76",
b"\xfb\xb3" : b"\x7b\x77",
b"\xfb\xb4" : b"\x7b\x78",
b"\xfb\xb5" : b"\x7b\x79",
b"\xfb\xb6" : b"\x7b\x7a",
b"\xfb\xb7" : b"\x7b\x7b",
b"\xfb\xb8" : b"\x7b\x7c",
b"\xfb\xb9" : b"\x7b\x7d",
b"\xfb\xba" : b"\x7b\x7e",
b"\xfb\xbb" : b"\x7c\x21",
b"\xfb\xbc" : b"\x7c\x22",
b"\xfb\xbd" : b"\x7c\x23",
b"\xfb\xbe" : b"\x7c\x24",
b"\xfb\xbf" : b"\x7c\x25",
b"\xfb\xc0" : b"\x7c\x26",
b"\xfb\xc1" : b"\x7c\x27",
b"\xfb\xc2" : b"\x7c\x28",
b"\xfb\xc3" : b"\x7c\x29",
b"\xfb\xc4" : b"\x7c\x2a",
b"\xfb\xc5" : b"\x7c\x2b",
b"\xfb\xc6" : b"\x7c\x2c",
b"\xfb\xc7" : b"\x7c\x2d",
b"\xfb\xc8" : b"\x7c\x2e",
b"\xfb\xc9" : b"\x7c\x2f",
b"\xfb\xca" : b"\x7c\x30",
b"\xfb\xcb" : b"\x7c\x31",
b"\xfb\xcc" : b"\x7c\x32",
b"\xfb\xcd" : b"\x7c\x33",
b"\xfb\xce" : b"\x7c\x34",
b"\xfb\xcf" : b"\x7c\x35",
b"\xfb\xd0" : b"\x7c\x36",
b"\xfb\xd1" : b"\x7c\x37",
b"\xfb\xd2" : b"\x7c\x38",
b"\xfb\xd3" : b"\x7c\x39",
b"\xfb\xd4" : b"\x7c\x3a",
b"\xfb\xd5" : b"\x7c\x3b",
b"\xfb\xd6" : b"\x7c\x3c",
b"\xfb\xd7" : b"\x7c\x3d",
b"\xfb\xd8" : b"\x7c\x3e",
b"\xfb\xd9" : b"\x7c\x3f",
b"\xfb\xda" : b"\x7c\x40",
b"\xfb\xdb" : b"\x7c\x41",
b"\xfb\xdc" : b"\x7c\x42",
b"\xfb\xdd" : b"\x7c\x43",
b"\xfb\xde" : b"\x7c\x44",
b"\xfb\xdf" : b"\x7c\x45",
b"\xfb\xe0" : b"\x7c\x46",
b"\xfb\xe1" : b"\x7c\x47",
b"\xfb\xe2" : b"\x7c\x48",
b"\xfb\xe3" : b"\x7c\x49",
b"\xfb\xe4" : b"\x7c\x4a",
b"\xfb\xe5" : b"\x7c\x4b",
b"\xfb\xe6" : b"\x7c\x4c",
b"\xfb\xe7" : b"\x7c\x4d",
b"\xfb\xe8" : b"\x7c\x4e",
b"\xfb\xe9" : b"\x7c\x4f",
b"\xfb\xea" : b"\x7c\x50",
b"\xfb\xeb" : b"\x7c\x51",
b"\xfb\xec" : b"\x7c\x52",
b"\xfb\xed" : b"\x7c\x53",
b"\xfb\xee" : b"\x7c\x54",
b"\xfb\xef" : b"\x7c\x55",
b"\xfb\xf0" : b"\x7c\x56",
b"\xfb\xf1" : b"\x7c\x57",
b"\xfb\xf2" : b"\x7c\x58",
b"\xfb\xf3" : b"\x7c\x59",
b"\xfb\xf4" : b"\x7c\x5a",
b"\xfb\xf5" : b"\x7c\x5b",
b"\xfb\xf6" : b"\x7c\x5c",
b"\xfb\xf7" : b"\x7c\x5d",
b"\xfb\xf8" : b"\x7c\x5e",
b"\xfb\xf9" : b"\x7c\x5f",
b"\xfb\xfa" : b"\x7c\x60",
b"\xfb\xfb" : b"\x7c\x61",
b"\xfb\xfc" : b"\x7c\x62",
b"\xfc\x40" : b"\x7c\x63",
b"\xfc\x41" : b"\x7c\x64",
b"\xfc\x42" : b"\x7c\x65",
b"\xfc\x43" : b"\x7c\x66",
b"\xfc\x44" : b"\x7c\x67",
b"\xfc\x45" : b"\x7c\x68",
b"\xfc\x46" : b"\x7c\x69",
b"\xfc\x47" : b"\x7c\x6a",
b"\xfc\x48" : b"\x7c\x6b",
b"\xfc\x49" : b"\x7c\x6c",
b"\xfc\x4a" : b"\x7c\x6d",
b"\xfc\x4b" : b"\x7c\x6e",
}

_kana_fulltohalf = {
u'\u3001':u'\uff64',
u'\u3002':u'\uff61',
u'\u30fb':u'\uff65',
u'\u30fc':u'\uff70',
u'\u300c':u'\uff62',
u'\u300d':u'\uff63',
u'\u30a1':u'\uff67',
u'\u30a2':u'\uff71',
u'\u30a3':u'\uff68',
u'\u30a4':u'\uff72',
u'\u30a5':u'\uff69',
u'\u30a6':u'\uff73',
u'\u30a7':u'\uff6a',
u'\u30a8':u'\uff74',
u'\u30a9':u'\uff6b',
u'\u30aa':u'\uff75',
u'\u30ab':u'\uff76',
u'\u30ac':u'\uff76\uff9e',
u'\u30ad':u'\uff77',
u'\u30ae':u'\uff77\uff9e',
u'\u30af':u'\uff78',
u'\u30b0':u'\uff78\uff9e',
u'\u30b1':u'\uff79',
u'\u30b2':u'\uff79\uff9e',
u'\u30b3':u'\uff7a',
u'\u30b4':u'\uff7a\uff9e',
u'\u30b5':u'\uff7b',
u'\u30b6':u'\uff7b\uff9e',
u'\u30b7':u'\uff7c',
u'\u30b8':u'\uff7c\uff9e',
u'\u30b9':u'\uff7d',
u'\u30ba':u'\uff7d\uff9e',
u'\u30bb':u'\uff7e',
u'\u30bc':u'\uff7e\uff9e',
u'\u30bd':u'\uff7f',
u'\u30be':u'\uff7f\uff9e',
u'\u30bf':u'\uff80',
u'\u30c0':u'\uff80\uff9e',
u'\u30c1':u'\uff81',
u'\u30c2':u'\uff81\uff9e',
u'\u30c3':u'\uff6f',
u'\u30c4':u'\uff82',
u'\u30c5':u'\uff82\uff9e',
u'\u30c6':u'\uff83',
u'\u30c7':u'\uff83\uff9e',
u'\u30c8':u'\uff84',
u'\u30c9':u'\uff84\uff9e',
u'\u30ca':u'\uff85',
u'\u30cb':u'\uff86',
u'\u30cc':u'\uff87',
u'\u30cd':u'\uff88',
u'\u30ce':u'\uff89',
u'\u30cf':u'\uff8a',
u'\u30d0':u'\uff8a\uff9e',
u'\u30d1':u'\uff8a\uff9f',
u'\u30d2':u'\uff8b',
u'\u30d3':u'\uff8b\uff9e',
u'\u30d4':u'\uff8b\uff9f',
u'\u30d5':u'\uff8c',
u'\u30d6':u'\uff8c\uff9e',
u'\u30d7':u'\uff8c\uff9f',
u'\u30d8':u'\uff8d',
u'\u30d9':u'\uff8d\uff9e',
u'\u30da':u'\uff8d\uff9f',
u'\u30db':u'\uff8e',
u'\u30dc':u'\uff8e\uff9e',
u'\u30dd':u'\uff8e\uff9f',
u'\u30de':u'\uff8f',
u'\u30df':u'\uff90',
u'\u30e0':u'\uff91',
u'\u30e1':u'\uff92',
u'\u30e2':u'\uff93',
u'\u30e3':u'\uff6c',
u'\u30e4':u'\uff94',
u'\u30e5':u'\uff6d',
u'\u30e6':u'\uff95',
u'\u30e7':u'\uff6e',
u'\u30e8':u'\uff96',
u'\u30e9':u'\uff97',
u'\u30ea':u'\uff98',
u'\u30eb':u'\uff99',
u'\u30ec':u'\uff9a',
u'\u30ed':u'\uff9b',
u'\u30ef':u'\uff9c',
u'\u30f2':u'\uff66',
u'\u30f3':u'\uff9d',
u'\u30f4':u'\uff73\uff9e',
}

_kana_halftofull = dict((v, k) for k, v in _kana_fulltohalf.items())


_fulltohalf = {
u'\uff01':u'!',	# EXCLAMATION MARK
u'\uff02':u'"',	# QUOTATION MARK
u'\uff03':u'#',	# NUMBER SIGN
u'\uff04':u'$',	# DOLLAR SIGN
u'\uff05':u'%',	# PERCENT SIGN
u'\uff06':u'&',	# AMPERSAND
u'\uff07':u"'",	# APOSTROPHE
u'\uff08':u'(',	# LEFT PARENTHESIS
u'\uff09':u')',	# RIGHT PARENTHESIS
u'\uff0a':u'*',	# ASTERISK
u'\uff0a':u'*',	# FORMS LIGHT VERTICAL
u'\uff0b':u'+',	# PLUS SIGN
u'\uff0c':u',',	# COMMA
u'\uff0d':u'-',	# HYPHEN-MINUS
u'\uff0e':u'.',	# FULL STOP
u'\uff0f':u'/',	# SOLIDUS
u'\uff10':u'0',	# DIGIT ZERO
u'\uff11':u'1',	# DIGIT ONE
u'\uff12':u'2',	# DIGIT TWO
u'\uff13':u'3',	# DIGIT THREE
u'\uff14':u'4',	# DIGIT FOUR
u'\uff15':u'5',	# DIGIT FIVE
u'\uff16':u'6',	# DIGIT SIX
u'\uff17':u'7',	# DIGIT SEVEN
u'\uff18':u'8',	# DIGIT EIGHT
u'\uff19':u'9',	# DIGIT NINE
u'\uff1a':u':',	# COLON
u'\uff1b':u';',	# SEMICOLON
u'\uff1c':u'<',	# LESS-THAN SIGN
u'\uff1d':u'=',	# EQUALS SIGN
u'\uff1e':u'>',	# GREATER-THAN SIGN
u'\uff1f':u'?',	# QUESTION MARK
u'\uff20':u'@',	# COMMERCIAL AT
u'\uff21':u'A',	# LATIN CAPITAL LETTER A
u'\uff22':u'B',	# LATIN CAPITAL LETTER B
u'\uff23':u'C',	# LATIN CAPITAL LETTER C
u'\uff24':u'D',	# LATIN CAPITAL LETTER D
u'\uff25':u'E',	# LATIN CAPITAL LETTER E
u'\uff26':u'F',	# LATIN CAPITAL LETTER F
u'\uff27':u'G',	# LATIN CAPITAL LETTER G
u'\uff28':u'H',	# LATIN CAPITAL LETTER H
u'\uff29':u'I',	# LATIN CAPITAL LETTER I
u'\uff2a':u'J',	# LATIN CAPITAL LETTER J
u'\uff2b':u'K',	# LATIN CAPITAL LETTER K
u'\uff2c':u'L',	# LATIN CAPITAL LETTER L
u'\uff2d':u'M',	# LATIN CAPITAL LETTER M
u'\uff2e':u'N',	# LATIN CAPITAL LETTER N
u'\uff2f':u'O',	# LATIN CAPITAL LETTER O
u'\uff30':u'P',	# LATIN CAPITAL LETTER P
u'\uff31':u'Q',	# LATIN CAPITAL LETTER Q
u'\uff32':u'R',	# LATIN CAPITAL LETTER R
u'\uff33':u'S',	# LATIN CAPITAL LETTER S
u'\uff34':u'T',	# LATIN CAPITAL LETTER T
u'\uff35':u'U',	# LATIN CAPITAL LETTER U
u'\uff36':u'V',	# LATIN CAPITAL LETTER V
u'\uff37':u'W',	# LATIN CAPITAL LETTER W
u'\uff38':u'X',	# LATIN CAPITAL LETTER X
u'\uff39':u'Y',	# LATIN CAPITAL LETTER Y
u'\uff3a':u'Z',	# LATIN CAPITAL LETTER Z
u'\uff3b':u'[',	# LEFT SQUARE BRACKET
#u'\uff3c':u'\\',	# REVERSE SOLIDUS
u'\uff3d':u']',	# RIGHT SQUARE BRACKET
u'\uff3e':u'^',	# CIRCUMFLEX ACCENT
u'\uff3f':u'_',	# LOW LINE
u'\uff40':u'`',	# GRAVE ACCENT
u'\uff41':u'a',	# LATIN SMALL LETTER A
u'\uff42':u'b',	# LATIN SMALL LETTER B
u'\uff43':u'c',	# LATIN SMALL LETTER C
u'\uff44':u'd',	# LATIN SMALL LETTER D
u'\uff45':u'e',	# LATIN SMALL LETTER E
u'\uff46':u'f',	# LATIN SMALL LETTER F
u'\uff47':u'g',	# LATIN SMALL LETTER G
u'\uff48':u'h',	# LATIN SMALL LETTER H
u'\uff49':u'i',	# LATIN SMALL LETTER I
u'\uff4a':u'j',	# LATIN SMALL LETTER J
u'\uff4b':u'k',	# LATIN SMALL LETTER K
u'\uff4c':u'l',	# LATIN SMALL LETTER L
u'\uff4d':u'm',	# LATIN SMALL LETTER M
u'\uff4e':u'n',	# LATIN SMALL LETTER N
u'\uff4f':u'o',	# LATIN SMALL LETTER O
u'\uff50':u'p',	# LATIN SMALL LETTER P
u'\uff51':u'q',	# LATIN SMALL LETTER Q
u'\uff52':u'r',	# LATIN SMALL LETTER R
u'\uff53':u's',	# LATIN SMALL LETTER S
u'\uff54':u't',	# LATIN SMALL LETTER T
u'\uff55':u'u',	# LATIN SMALL LETTER U
u'\uff56':u'v',	# LATIN SMALL LETTER V
u'\uff57':u'w',	# LATIN SMALL LETTER W
u'\uff58':u'x',	# LATIN SMALL LETTER X
u'\uff59':u'y',	# LATIN SMALL LETTER Y
u'\uff5a':u'z',	# LATIN SMALL LETTER Z
u'\uff5b':u'{',	# LEFT CURLY BRACKET
u'\uff5c':u'|',	# VERTICAL LINE
u'\uff5d':u'}',	# RIGHT CURLY BRACKET
u'\uff5e':u'~',	# TILDE
u'\uffe0':u'\xa2',	# CENT SIGN
u'\uffe1':u'\xa3',	# POUND SIGN
u'\uffe2':u'\xac',	# NOT SIGN
u'\uffe5':u'\\',	# YEN SIGN
}

_halftofull = dict((v, k) for k, v in _fulltohalf.items())


def _is_jis(c):
     return 0x21 <= c <= 0x7e

def _is_euc(c):
     return 0xa1 <= c <= 0xfe

def _is_gaiji1(c):
     return 0xf0 <= c <= 0xf9

def _is_ibmgaiji1(c):
    return 0xfa <= c <= 0xfc

def _is_sjis1(c):
    if 0x81 <= c <= 0x9f:
        return True
    if 0xe0 <= c <= 0xef:
        return True
    if _is_gaiji1(c) or _is_ibmgaiji1(c):
         return True

def _is_sjis2(c):
    return (0x40 <= c <= 0xfc) and (c != 0x7f)
    
def _is_half_kana(c):
    return 0xa0 <= c <= 0xdf

def _utf8_len(c):
    if 0xc0 <= c <= 0xdf: return 2
    if 0xe0 <= c <= 0xef: return 3
    if 0xf0 <= c <= 0xf7: return 4
    if 0xf8 <= c <= 0xfb: return 5
    if 0xfc <= c <= 0xfd: return 6
    return 

def _is_utf8_trail(c):
    return 0x80 <= c <= 0xbf

def _jis_to_sjis(h, l):
    if h & 1:
        if l < 0x60:
            l += 0x1f
        else:             
            l += 0x20
    else:
        l += 0x7e

    if h < 0x5f:
        h = (h + 0xe1) >> 1
    else:
        h = (h + 0x161) >> 1
    
    return bytes([h & 0xff, l & 0xff])


def _jis_to_mskanji(h, l):
    c = h+l
    if c in _tbl_jis2mskanji:
        return _tbl_jis2mskanji[c]
    else:
        return _jis_to_sjis(h, l)

def _sjis_to_jis(h, l):
    if h < 0x9f:
        if l < 0x9f:
            h = (h << 1) - 0xe1
        else:
            h = (h << 1) - 0xe0
    else:
        if l < 0x9f:
            h = (h << 1) - 0x161
        else:
            h = (h << 1) - 0x160
    
    if l < 0x7f:
        l -= 0x1f
    elif l < 0x9f:
        l -= 0x20
    else:
        l -= 0x7e
    
    return bytes([h & 0xff, l & 0xff])


def _mskanji_to_jis(h, l):
    if _is_gaiji1(h):
        return CONV_FAILED

    c = bytes([h, l])
    if c in _tbl_mskanji2jis:
        return _tbl_mskanji2jis[c]
    else:
        return _sjis_to_jis(h, l)
    

def guess(s):
    if not s:
        return ASCII

    # check BOM
    bom = s[:2]
    if bom == b"\xff\xfe":
        return UTF16_LE
    if bom == b"\xfe\xff":
        return UTF16_BE
    if s[:3] == b"\xef\xbb\xbf":
        return UTF8
    
    # check JIS
    if 0x1b in s:
        return JIS

    # check ascii
    if max(s) < 0x80:
        return ASCII

    ascii = 1
    sjis = jis = euc = utf8 = 0
    bad_ascii = bad_sjis = bad_euc = bad_utf8 = 0
    sjis_error = euc_error = utf8_error = 0
    slen = len(s)

    # check SJIS
    i = 0
    halfkana = 0
    while i < slen:
        c = s[i]
        if _is_half_kana(c):
            # half-kana
            sjis += 7
            halfkana += 1
        else:
            if halfkana == 1:
                # single halfwidth-kana is bad sign.
                bad_sjis += 7
            halfkana = 0
            
            if _is_sjis1(c):
                if c == 0x8e:
                    # looks like euc.
                    bad_sjis += 10

                if (i+1 < slen) and _is_sjis2(s[i+1]):
                    sjis += 16
                    i += 1
                else:
                    sjis_error = 1
                    break
            elif c >= 0x80:
                sjis_error = 1
                break
        i += 1
        

    # check EUC
    i = 0
    halfkana = 0
    while i < slen:
        c = s[i]
        if c == 0x8e:
            if (i+1 < slen) and _is_half_kana(s[i+1]):
                euc += 8
                i += 1
                halfkana += 1
            else:
                euc_error = 1
                break
        else:
            if halfkana == 1:
                bad_euc += 5
            halfkana = 0

            if _is_euc(c):
                if (i+1 < slen) and _is_euc(s[i+1]):
                    euc += 16
                    i += 1
                else:
                    euc_error = 1
                    break
            elif c == 0x8f:
                if (i+2 < slen) and _is_euc(s[i+1]) and _is_euc(s[i+2]):
                    euc += 16
                    i += 2
                else:
                    euc_error = 1
                    break
            elif c >= 0x80:
                euc_error = 1
                break

        i += 1

    # check UTF8
    i = 0
    halfkana = 0
    while i < slen:
        c = s[i]
        clen = _utf8_len(c)
        if clen:
            if i+clen-1 >= slen:
                utf8_error = 1
                break

            for j in range(i+1, i+clen):
                if not _is_utf8_trail(s[j]):
                    utf8_error = 1
                    break
            
            if utf8_error:
                break
            
            utf8 += 16*(clen*2//3)+1
            i += clen

        elif c >= 0x80:
            utf8_error = 1
            break
        
        else:
            i += 1

#    print ">>>>>>>>>>>>>>>>>>>>>>>>>>"
#    print sjis_error, bad_sjis, sjis
#    print euc_error, bad_euc, euc
#    print utf8_error, bad_utf8, utf8

    if sjis_error and euc_error and utf8_error:
        return UNKNOWN

    if sjis_error:
        if euc_error:
            return UTF8
        elif utf8_error:
            return EUC
        if euc-bad_euc > utf8-bad_utf8:
            return EUC
        else:
            return UTF8
            
    if euc_error:
        if sjis_error:
            return UTF8
        elif utf8_error:
            return SJIS
        if sjis-bad_sjis > utf8-bad_utf8:
            return SJIS
        else:
            return UTF8
            
    if utf8_error:
        if sjis_error:
            return EUC
        elif sjis_error:
            return EUC
        if sjis-bad_sjis > euc-bad_euc:
            return SJIS
        else:
            return EUC
    
    if sjis-bad_sjis >= euc-bad_euc:
        if utf8-bad_utf8 >= sjis-bad_sjis:
            return UTF8
        else:
            return SJIS
    else:
        if utf8-bad_utf8 >= euc-bad_euc:
            return UTF8
        else:
            return EUC


def euctosjis(s):
    ret = []
    slen = len(s)
    i = 0
    while i < slen:
        if (i+1 < slen) and _is_euc(s[i]) and _is_euc(s[i+1]):
            c1 = s[i] & 0x7f
            c2 = s[i+1] & 0x7f
            ret.append(_jis_to_mskanji(c1, c2))
            i += 2
        elif (i+1 < slen) and s[i] == 0x8e and _is_half_kana(s[i+1]):
            ret.append(s[i+1:i+2])
            i += 2
        else:
            ret.append(s[i:i+1])
            i += 1
    return b"".join(ret)


def jistosjis(s):
    ret = []
    slen = len(s)
    i = 0
    NORMAL, KANJI, HALFKANA = range(0, 3)
    mode = NORMAL
    
    while i < slen:
        if s[i:i+3] in (b"\x1b$@", b"\x1b$B"):
            mode = KANJI
            i += 3
        elif s[i:i+4] == b"\x1b$(O":
            mode = KANJI
            i += 4
        elif s[i:i+3] in (b"\x1b(B", b"\x1b(J"):
            mode = NORMAL;
            i += 3
        elif s[i:i+3] == b"\x1b(I":
            mode = HALFKANA
            i += 3
        elif s[i] == 0x0e:
            mode = HALFKANA
            i += 1
        elif s[i] == 0x0f:
            mode = NORMAL
            i += 1
        elif mode == KANJI and (i+1) < slen:
            ret.append(_jis_to_mskanji(s[i], s[i+1]))
            i += 2
        elif mode == HALFKANA:
            ret.append(bytes([(s[i] | 0x80) & 0xff]))
            i += 1
        else:
            ret.append(s[i:i+1])
            i += 1
    return b"".join(ret)



def sjistoeuc(s):
    ret = []
    slen = len(s)
    i = 0
    
    while i < slen:
        if _is_sjis1(s[i]) and (i+1) < slen:
            c1, c2 = _mskanji_to_jis(s[i], s[i+1])

            ret.append(bytes([(c1 | 0x80) & 0xff, (c2 | 0x80) & 0xff]))
            i += 2
        elif _is_half_kana(s[i]):
            ret.append(b"\x8e")
            ret.append(s[i:i+1])
            i += 1
        else:
            ret.append(s[i:i+1])
            i += 1

    return b"".join(ret)
    
def sjistojis(s):
    ret = []
    slen = len(s)
    i = 0

    NORMAL, KANJI, HALFKANA = range(0, 3)
    mode = NORMAL
    
    while i < slen:
        if _is_sjis1(s[i]) and (i+1) < slen:
            c = _mskanji_to_jis(s[i], s[i+1])
            if mode != KANJI:
                mode = KANJI;
                ret.append(b"\x1b$B")

            ret.append(c)
            i += 2

        elif _is_half_kana(s[i]):
            if mode != HALFKANA:
                mode = HALFKANA;
                ret.append(b"\x1b(I")
                
            ret.append(bytes([(s[i] & 0x7f)]))
            i += 1

        else:
            if mode != NORMAL:
                mode = NORMAL
                ret.append(b"\x1b(B")

            ret.append(s[i:i+1])
            i += 1
    
    if mode != NORMAL:
        ret.append(b"\x1b(B")
    return b"".join(ret)


def jistoeuc(s):
    return sjistoeuc(jistosjis(s))

def euctojis(s):
    return sjistojis(euctosjis(s))

def _callsub(s, _re, d):
    def _rep(m, d=d):
        c = m.group(0)
        return d[c]
    return _re.sub(_rep, s)

_re_kana_full = re.compile(
    u"|".join(u'%s' % c for c in _kana_fulltohalf.keys()))

def kanatohalf(s):
    return _callsub(s, _re_kana_full, _kana_fulltohalf)

_re_kana_half = re.compile(
    u"|".join(u'%s' % c for c in _kana_halftofull.keys()))

def kanatofull(s):
    return _callsub(s, _re_kana_half, _kana_halftofull)

_re_full = re.compile(
    u"|".join(u'%s' % re.escape(c) for c in _halftofull.keys()))
def tofull(s):
    return _callsub(s, _re_full, _halftofull)

_re_half = re.compile(
    u"|".join(u'%s' % re.escape(c) for c in _fulltohalf.keys()))
def tohalf(s):
    return _callsub(s, _re_half, _fulltohalf)



_from_dates = [
    (1868, 1, 1),
    (1912, 7, 30),
    (1926, 12, 25),
    (1989, 1, 8)
]
_nengo = [
u" ",
u'\u660e\u6cbb',
u'\u5927\u6b63',
u'\u662d\u548c',
u'\u5e73\u6210',
]

_nengo_c = u" MTSH"

def getnengo(y, m, d, letter=False):
    if y < 1868:
        raise ValueError()
        
    n = bisect.bisect(_from_dates, (y, m, d))
    if letter:
        nengo = _nengo_c[n]
    else:
        nengo = _nengo[n]
    return nengo, y - _from_dates[n-1][0] + 1


def heiseitoyear(h):
    if h <= 0: raise ValueError()
    return 1989+h-1


def showatoyear(s):
    if s <= 0: raise ValueError()
    return 1926+s-1


def taishotoyear(t):
    if t <= 0: raise ValueError()
    return 1912+t-1


def meijitoyear(m):
    if m <= 0: raise ValueError()
    return 1868+m-1


_re_word = re.compile(u".[。、,.!;]|[a-zA-Z0-9_]+|.")

def _splitword(s):
    # todo: surrogate pair/combining character(e.g. U+309A)
    slen = len(s)
    f = pos = 0
    for m in _re_word.finditer(s):
        yield m.group()

def _calccols(s):
    d = {'Na':1, 'N':1, 'H':1, 'W':2, 'F':2, 'A':2}
    ret = [d[unicodedata.east_asian_width(c)] for c in s]
    return ret

    
def wrap(s, maxcol):
    if maxcol < 1:
        raise ValueError("maxcol must be greater than zero")
        
    lines = s.splitlines()
    for line in lines:
        words = []
        col = 0
        for word in _splitword(line):
            cols = _calccols(word)
            wordlen = sum(cols)
            if col+wordlen > maxcol:
                if col > 0:
                    yield u"".join(words)
                    col = 0
                    words = []

                for char, w in zip(word, cols):
                    words.append(char)
                    col += w
                    if col >= maxcol:
                        yield u"".join(words)
                        col = 0
                        words = []
            else:
                words.append(word)
                col += wordlen
        if col:
            yield u"".join(words)


