# -*- coding: utf-8 -*-
""" Character mapping codec which removes accents from latin-1 characters

Written by Skip Montanaro (skip@pobox.com) using the autogenerated cp1252
codec as an example.

(c) Copyright CNRI, All Rights Reserved. NO WARRANTY.
(c) Copyright 2000 Guido van Rossum.

"""

import codecs

### Decoding Map

decoding_map = codecs.make_identity_dict(range(256))
for x in range(0x80, 0xa0):
    decoding_map[x] = ord('?') # undefined
decoding_map.update({
    0x00a1: ord('!'), # ¡
    0x00a2: ord('c'), # ¢
    0x00a3: ord('#'), # £
    0x00a4: ord('o'), # ¤
    0x00a5: ord('Y'), # ¥
    0x00a6: ord('|'), # ¦
    0x00a7: ord('S'), # §
    0x00a8: ord('"'), # ¨
    0x00a9: ord('c'), # ©
    0x00aa: ord('a'), # ª
    0x00ab: ord('<'), # «
    0x00ac: ord('-'), # ¬
    0x00ad: ord('-'), # ­
    0x00ae: ord('R'), # ®
    0x00af: ord('-'), # ¯
    0x00b0: ord('o'), # °
    0x00b1: ord('+'), # ±
    0x00b2: ord('2'), # ²
    0x00b3: ord('3'), # ³
    0x00b4: ord("'"), # ´
    0x00b5: ord('u'), # µ
    0x00b6: ord('P'), # ¶
    0x00b7: ord('-'), # ·
    0x00b8: ord(','), # ¸
    0x00b9: ord('1'), # ¹
    0x00ba: ord('o'), # º
    0x00bb: ord('>'), # »
    0x00bc: ord('1'), # ¼
    0x00bd: ord('2'), # ½
    0x00be: ord('3'), # ¾
    0x00bf: ord('?'), # ¿
    0x00c0: ord('A'), # À
    0x00c1: ord('A'), # Á
    0x00c2: ord('A'), # Â
    0x00c3: ord('A'), # Ã
    0x00c4: ord('A'), # Ä
    0x00c5: ord('A'), # Å
    0x00c6: ord('A'), # Æ
    0x00c7: ord('C'), # Ç
    0x00c8: ord('E'), # È
    0x00c9: ord('E'), # É
    0x00ca: ord('E'), # Ê
    0x00cb: ord('E'), # Ë
    0x00cc: ord('I'), # Ì
    0x00cd: ord('I'), # Í
    0x00ce: ord('I'), # Î
    0x00cf: ord('I'), # Ï
    0x00d0: ord('D'), # Ð
    0x00d1: ord('N'), # Ñ
    0x00d2: ord('O'), # Ò
    0x00d3: ord('O'), # Ó
    0x00d4: ord('O'), # Ô
    0x00d5: ord('O'), # Õ
    0x00d6: ord('O'), # Ö
    0x00d7: ord('X'), # ×
    0x00d8: ord('O'), # Ø
    0x00d9: ord('U'), # Ù
    0x00da: ord('U'), # Ú
    0x00db: ord('U'), # Û
    0x00dc: ord('U'), # Ü
    0x00dd: ord('Y'), # Ý
    0x00de: ord('P'), # Þ
    0x00df: ord('B'), # ß
    0x00e0: ord('a'), # à
    0x00e1: ord('a'), # á
    0x00e2: ord('a'), # â
    0x00e3: ord('a'), # ã
    0x00e4: ord('a'), # ä
    0x00e5: ord('a'), # å
    0x00e6: ord('a'), # æ
    0x00e7: ord('c'), # ç
    0x00e8: ord('e'), # è
    0x00e9: ord('e'), # é
    0x00ea: ord('e'), # ê
    0x00eb: ord('e'), # ë
    0x00ec: ord('i'), # ì
    0x00ed: ord('i'), # í
    0x00ee: ord('i'), # î
    0x00ef: ord('i'), # ï
    0x00f0: ord('o'), # ð
    0x00f1: ord('n'), # ñ
    0x00f2: ord('o'), # ò
    0x00f3: ord('o'), # ó
    0x00f4: ord('o'), # ô
    0x00f5: ord('o'), # õ
    0x00f6: ord('o'), # ö
    0x00f7: ord('/'), # ÷
    0x00f8: ord('o'), # ø
    0x00f9: ord('u'), # ù
    0x00fa: ord('u'), # ú
    0x00fb: ord('u'), # û
    0x00fc: ord('u'), # ü
    0x00fd: ord('y'), # ý
    0x00fe: ord('p'), # þ
    0x00ff: ord('y'), # ÿ
})

### Encoding Map

encoding_map = codecs.make_identity_dict(range(256))


def register_codec():
    class Codec(codecs.Codec):
        def decode(self, input, errors='strict'):
            return codecs.charmap_decode(input, errors, decoding_map)

        def encode(self, input, errors='strict'):
            return codecs.charmap_encode(input, errors, encoding_map)

    class StreamWriter(Codec, codecs.StreamWriter):
        pass

    class StreamReader(Codec, codecs.StreamReader):
        pass

    def getregentry(encoding):
        if encoding != 'latscii':
            return None
        return (Codec().encode,
                Codec().decode,
                StreamReader,
                StreamWriter)
    codecs.register(getregentry)

    def latscii_error(uerr):
        text = uerr.object[uerr.start:uerr.end]
        ret = ''

        for c in text:
            key = ord(c)
            try:
                ret += unichr(decoding_map[key])
            except KeyError:
                handler = codecs.lookup_error('replace')
                return handler(uerr)

        return ret, uerr.end
    codecs.register_error('replacelatscii', latscii_error)
