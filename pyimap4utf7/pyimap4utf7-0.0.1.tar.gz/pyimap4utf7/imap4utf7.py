#!/usr/bin/env python
import binascii
import codecs


def modified_base64(s):
    s = s.encode('utf-16be')
    return binascii.b2a_base64(s).rstrip('\n=').replace('/', ',')


def encode(s):
    r = []
    other_chars = []
    for c in s:
        ordC = ord(c)
        if 0x20 <= ordC <= 0x7e:
            if other_chars:
                r.append('&{0}-'.format(modified_base64(''.join(other_chars))))
            del other_chars[:]
            r.append(c)
            if c == '&':
                r.append('-')
        else:
            other_chars.append(c)
    if other_chars:
        r.append('&{0}-'.format(modified_base64(''.join(other_chars))))
        del other_chars[:]
    return str(''.join(r))


def modified_unbase64(s):
    b = binascii.a2b_base64(s.replace(',', '/') + '===')
    return unicode(b, 'utf-16be')


def decode(s):
    r = []
    decode_chars = []
    for c in s:
        if c == '&' and not decode_chars:
            decode_chars.append('&')
        elif c == '-' and decode_chars:
            if len(decode_chars) == 1:
                r.append('&')
            else:
                r.append(modified_unbase64(''.join(decode_chars[1:])))
            decode_chars = []
        elif decode_chars:
            decode_chars.append(c)
        else:
            r.append(c)
    if decode_chars:
        r.append(modified_unbase64(''.join(decode_chars[1:])))
    bin_str = ''.join(r)
    return bin_str
