# coding: utf-8
from __future__ import unicode_literals, print_function
from . import csp
from pyasn1.type import univ, useful, char, tag, constraint
from pyasn1.codec.der import encoder, decoder
from pyasn1_modules import rfc2459, rfc2315
from base64 import b64decode
from datetime import timedelta
import sys
if sys.version_info >= (3,):
        unicode = str
        long = int
else:
        unicode = unicode


def autopem(cert):
    if cert[:3] == b'---':
        s = ''.join(l for l in cert.splitlines() if not l.startswith('----'))
        return b64decode(s)
    else:
        return cert


def _deep_find(lst, oid):
    for attr in lst:
        if isinstance(attr, list) and _deep_find(attr, oid):
            return True
        elif attr[0] == oid:
            return True
    return False


def set_q_defaults(params):
    attrs = params.get('Attributes', [])[:]
    defaults = {
        '1.2.643.100.1': '0' * 13,
        '1.2.643.100.3': '0' * 11,
        '1.2.643.3.131.1.1': '0' * 12,
    }
    for oid in defaults:
        if not _deep_find(attrs, oid):
            attrs.append((oid, defaults[oid]))
    params['Attributes'] = attrs

    raw = params.get('RawExtensions', [])[:]
    if not any(oid == '1.2.643.100.111' for (oid, _, _) in raw):
        extstr = encoder.encode(char.UTF8String('"КриптоПро CSP" (версия 3.6)'.encode('utf-8')))
        raw.append(('1.2.643.100.111', extstr, False))
    params['RawExtensions'] = raw


class CertAttribute(object):
    """Атрибут запроса на сертификат

    в закодированном виде добавляется в запрос методом
    CertRequest.add_attribute()
    """
    def __init__(self, oid, values):
        """@todo: to be defined """
        self.oid = oid.encode('ascii')
        self.vals = [encoder.encode(v) for v in values]

    def add_to(self, req):
        n = req.add_attribute(self.oid)
        for v in self.vals:
            req.add_attribute_value(n, v)


class CertValidity(CertAttribute):
    """Атрибут для установки интервала действия серта в запросе"""

    def __init__(self, not_before, not_after):
        """@todo: to be defined """
        val = univ.Sequence()
        for i, x in enumerate((not_before, not_after)):
            val.setComponentByPosition(i, useful.UTCTime(x.strftime('%y%m%d%H%M%SZ')))
        super(CertValidity, self).__init__('1.2.643.2.4.1.1.1.1.2', [val])


class CertExtensions(CertAttribute):
    """Атрибут для задания расширений сертификата"""

    def __init__(self, exts):
        """@todo: to be defined """
        val = univ.SequenceOf()
        for i, ext in enumerate(exts):
            val.setComponentByPosition(i, ext.asn)
        super(CertExtensions, self).__init__(csp.szOID_CERT_EXTENSIONS, [val])


class CertExtension(object):
    def __init__(self, oid, value, critical=False):
        """Общий класс для всех видов расширений

        :oid: OID расширения
        :value: значение в ASN.1

        """
        self.asn = rfc2459.Extension()
        self.asn.setComponentByName('extnID', univ.ObjectIdentifier(oid))
        self.asn.setComponentByName('critical', univ.Boolean(critical))
        self.asn.setComponentByName('extnValue', univ.OctetString(value))


class EKU(CertExtension):
    """Расширенное использование ключа"""

    def __init__(self, ekus):
        """Создание EKU

        :ekus: список OID-ов расш. использования

        """
        val = rfc2459.ExtKeyUsageSyntax()
        for i, x in enumerate(ekus):
            val.setComponentByPosition(i, rfc2459.KeyPurposeId(str(x)))
        super(EKU, self).__init__(csp.szOID_ENHANCED_KEY_USAGE, encoder.encode(val))


class KeyUsage(CertExtension):
    """Расширенное использование ключа"""

    def __init__(self, mask):
        """Создание EKU

        :ekus: список OID-ов расш. использования

        """
        val = rfc2459.KeyUsage(str(','.join(mask)))
        super(KeyUsage, self).__init__(csp.szOID_KEY_USAGE, encoder.encode(val))


def _stupidAddress(s):
    res = univ.Sequence()
    res.setComponentByPosition(0, char.UTF8String(s))
    return res


class Attributes(object):
    """Набор пар (тип, значение)"""
    special_encs = {
        '1.2.643.100.1': (char.NumericString, 'ascii'),
        '1.2.643.100.3': (char.NumericString, 'ascii'),
        '1.2.643.3.131.1.1': (char.NumericString, 'ascii'),
        '2.5.4.6': (char.PrintableString, 'ascii'),
        '1.2.840.113549.1.9.1': (char.IA5String, 'ascii'),
        '2.5.4.16': (_stupidAddress, 'utf-8'),
    }

    def __init__(self, attrs):
        if isinstance(attrs, list):
            self.asn = rfc2459.Name()
            vals = rfc2459.RDNSequence()

            for (i, attr) in enumerate(attrs):
                if not isinstance(attr, list):
                    attr = [attr]
                pairset = rfc2459.RelativeDistinguishedName()
                for (j, (oid, val)) in enumerate(attr):
                    pair = rfc2459.AttributeTypeAndValue()
                    pair.setComponentByName('type', rfc2459.AttributeType(str(oid)))
                    code, enc = self.special_encs.get(oid, (char.UTF8String, 'utf-8'))
                    pair.setComponentByName('value',
                                            rfc2459.AttributeValue(
                                                univ.OctetString(encoder.encode(code(unicode(val).encode(enc, 'replace'))))))

                    pairset.setComponentByPosition(j, pair)

                vals.setComponentByPosition(i, pairset)

            self.asn.setComponentByPosition(0, vals)
        else:
            self.asn = attrs

    def encode(self):
        return encoder.encode(self.asn)

    @classmethod
    def load(cls, value):
        return(cls(decoder.decode(value, asn1Spec=rfc2459.Name())[0]))

    def decode(self):
        res = []
        for rdn in self.asn[0]:
            item = []
            for dn in rdn:
                oid = unicode(dn[0])
                a = decoder.decode(dn[1])[0]
                if oid == '2.5.4.16':
                    s = ' '.join(unicode(x) for x in a)
                else:
                    s = unicode(a)
                item.append((oid, s))
            if len(item) != 1:
                res.append(item)
            else:
                res.append(item[0])
        return res


class CertificateInfo(object):
    def __init__(self, certdata):
        """@todo: Docstring for __init__

        :certdata: @todo
        :returns: @todo

        """

        self.asn = decoder.decode(certdata, asn1Spec=rfc2459.Certificate())[0]

    def EKU(self):
        for ext in self.asn[0].getComponentByName('extensions') or []:
            if ext[0] == rfc2459.id_ce_extKeyUsage:
                res = decoder.decode(ext.getComponentByName('extnValue'))[0]
                res = decoder.decode(res, asn1Spec=rfc2459.ExtKeyUsageSyntax())[0]
                return list(str(x) for x in res)
        return []


class SubjectAltName(CertExtension):
    """Расширенное использование ключа"""

    def x400Address(self, val):
        return decoder.decode(val,
                              asn1Spec=rfc2459.ORAddress().subtype(implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 3)))

    def ediPartyName(self, val):
        res = rfc2459.EDIPartyName(
        ).subtype(implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 5))
        if isinstance(val, tuple):
            val0 = rfc2459.DirectoryString(
            ).subtype(implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 0))
            val0.setComponentByName('utf8String', unicode(val[0]).encode('utf-8'))
            res.setComponentByName('nameAssigner', val0)
            val1 = rfc2459.DirectoryString(
            ).subtype(implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 1))
            val1.setComponentByName('utf8String', unicode(val[1]).encode('utf-8'))
            res.setComponentByName('partyName', val1)
        else:
            val1 = rfc2459.DirectoryString(
            ).subtype(implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 1))
            val1.setComponentByName('utf8String', unicode(val).encode('utf-8'))
            res.setComponentByName('partyName', val1)
        return res

    def otherName(self, val):
        res = rfc2459.AnotherName(
        ).subtype(implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 0))
        res.setComponentByName('type-id', str(val[0]))
        res.setComponentByName('value', str(val[1]))
        return res

    def rfc822Name(self, st):
        '''
        :st: строка с именем

        '''
        return unicode(st).encode('cp1251', 'replace')

    dNSName = rfc822Name
    uniformResourceIdentifier = rfc822Name
    iPAddress = rfc822Name
    registeredID = rfc822Name

    def directoryName(self, rdn):
        '''
        :rdn: [(OID, value), (OID, value) ...]

        '''
        elt = rfc2459.Name().subtype(
            implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 4))
        elt.setComponentByName('', Attributes(rdn).asn[0])
        return elt

    def __init__(self, altnames):
        """Создание AltName

        :altnames: список вида [(тип, значение), (тип, значение), ]
            где значение в зависимости от типа:
                    'otherName' : ('OID', 'байтовая строка')
                    'ediPartyName' : ('строка', 'строка') или 'строка'
                    'x400Address' : 'байтовая строка'
                    'directoryName' : [('OID', 'строка'), ...]
                    'dNSName' : строка
                    'uniformResourceIdentifier' : строка
                    'iPAddress' : строка
                    'registeredID' : строка

        """
        val = rfc2459.SubjectAltName()
        for (i, (t, v)) in enumerate(altnames):
            gn = rfc2459.GeneralName()
            elt = getattr(self, t, None)
            assert elt is not None, 'unsupported element type {0}'.format(t)
            gn.setComponentByName(t, elt(v))
            val.setComponentByPosition(i, gn)

        super(SubjectAltName, self).__init__(rfc2459.id_ce_subjectAltName, encoder.encode(val))


class CertificatePolicies(CertExtension):
    def __init__(self, policies):
        '''создане CertificatePolicies

        :policies: список вида [(OID, [(квалификатор, значение), ...]), ... ]
            OID - идент-р политики
            квалификатор - OID
            значение - произвольная информация в base64

        '''
        pass
        val = rfc2459.CertificatePolicies()
        for (i, (t, v)) in enumerate(policies or []):
            pol = rfc2459.PolicyInformation()
            pol.setComponentByPosition(0, rfc2459.CertPolicyId(str(t)))
            v = v or []
            if len(v):
                sq = univ.SequenceOf(componentType=rfc2459.PolicyQualifierInfo()
                                     ).subtype(subtypeSpec=constraint.ValueSizeConstraint(1, rfc2459.MAX))
                for n, (ident, qualif) in enumerate(v):
                    pqi = rfc2459.PolicyQualifierInfo()
                    pqi.setComponentByPosition(0, rfc2459.PolicyQualifierId(str(ident)))
                    pqi.setComponentByPosition(1, univ.OctetString(qualif))
                    sq.setComponentByPosition(n, pqi)
                pol.setComponentByPosition(1, sq)
            val.setComponentByPosition(i, pol)
        super(CertificatePolicies, self).__init__(rfc2459.id_ce_certificatePolicies,
                                                  encoder.encode(val))


class PKCS7Msg(object):
    """Парсинг свойств pkcs7 сообщения"""

    def __init__(self, data):
        """@todo: to be defined

        :data: @todo

        """
        self.asn = decoder.decode(data, asn1Spec=rfc2315.ContentInfo())[0]
        self.contentType = {
            '1.2.840.113549.1.7.1': rfc2315.Data,
            '1.2.840.113549.1.7.2': rfc2315.SignedData,
            '1.2.840.113549.1.7.3': rfc2315.EnvelopedData,
            '1.2.840.113549.1.7.4': rfc2315.SignedAndEnvelopedData,
            '1.2.840.113549.1.7.5': rfc2315.DigestedData,
            '1.2.840.113549.1.7.6': rfc2315.EncryptedData,
        }.get(str(self.asn[0]), None)

        assert self.contentType, 'Unsupported message content type'
        self.content = decoder.decode(self.asn[1], asn1Spec=self.contentType())[0]

    def data(self):
        return {}

    digestedData = data

    encryptedData = data

    def envelopedData(self):
        res = []
        for si in self.content.getComponentByName('recipientInfos'):
            info = si.getComponentByName('issuerAndSerialNumber')
            attrs = Attributes(info[0]).decode()
            sn = '{0:x}'.format(long(info[1]))
            res.append(dict(Issuer=attrs, SerialNumber=sn))
        return dict(RecipientInfos=res)

    def signedData(self):
        res = []
        for si in self.content.getComponentByName('signerInfos'):
            info = si.getComponentByName('issuerAndSerialNumber')
            attrs = Attributes(info[0]).decode()
            sn = '{0:x}'.format(long(info[1]))
            res.append(dict(Issuer=attrs, SerialNumber=sn))
        return dict(SignerInfos=res)

    def signedAndEnvelopedData(self):
        res = {}
        res.update(self.signedData())
        res.update(self.envelopedData())
        return res

    def abstract(self):
        ct = self.contentType.__name__
        ct = ct[0].lower() + ct[1:]
        res = dict(ContentType=ct)
        fun = getattr(self, ct, None)
        if fun is not None:
            res.update(fun())
        return res


if __name__ == '__main__':
    info = CertificateInfo(open('../examples/cer_test.cer', 'rb').read())
    print(info.EKU())
    print(info.asn.prettyPrint())
    # altnn = SubjectAltName([('otherName', ('1.2.3', 'aslkdj'))])
    # print(altnn.asn)
    # from pyasn1_modules.rfc2459 import id_qt_unotice as unotice, id_qt_cps as cps
    # test = CertificatePolicies([(unotice, []), (cps, [(cps, b64encode(b"alsdk"))])])
    # data = open('../examples/cer_test.cer', 'rb').read()
    # cert = decoder.decode(data, asn1Spec=rfc2459.Certificate())[0]
    # print(cert.prettyPrint())
    # ci = csp.CertInfo(csp.Cert(data))
    # xx = Attributes.decode(ci.issuer(False))
    # print(xx)
    # msg = PKCS7Msg(open('../examples/encrypted.p7s', 'rb').read())
    # print(msg.abstract())
