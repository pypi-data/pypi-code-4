#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import csp
from certutils import Attributes, CertValidity, KeyUsage, EKU,\
    CertExtensions, SubjectAltName, CertificatePolicies, PKCS7Msg, \
    CertExtension, CertificateInfo, autopem, set_q_defaults

import platform
from binascii import hexlify, unhexlify
from filetimes import filetime_from_dec
from datetime import datetime, timedelta


def gen_key(cont, local=True, silent=False):
    '''
    Создание контейнера и двух пар ключей в нем

    :cont: Имя контейнера (строка)
    :local: Если True, контейнер создается в локальном хранилище по умолчанию
    :silent: Если True, включает режим без диалоговых окон. Без аппаратного датчика случайных
        чисел в таком режиме контейнер создать невозможно!
        По умолчанию silent=False
    :returns: True, если операция успешна

    '''
    silent_flag = csp.CRYPT_SILENT if silent else 0
    provider = b"Crypto-Pro HSM CSP" if not local else None

    cont = bytes(cont)
    try:
        ctx = csp.Crypt(cont, csp.PROV_GOST_2001_DH, silent_flag, provider)
    except (ValueError, SystemError):

        if platform.system() == 'Linux' and local:
            cont = bytes(r'\\.\HDIMAGE\{0}'.format(cont))

        ctx = csp.Crypt(cont, csp.PROV_GOST_2001_DH, csp.CRYPT_NEWKEYSET |
                        silent_flag, provider)

    ctx.set_password(b'', csp.AT_KEYEXCHANGE)
    ctx.set_password(b'', csp.AT_SIGNATURE)
    try:
        key = ctx.get_key()
    except ValueError:
        key = ctx.create_key(csp.CRYPT_EXPORTABLE, csp.AT_SIGNATURE)

    assert key, 'NULL signature key'

    try:
        ekey = ctx.get_key(csp.AT_KEYEXCHANGE)
    except ValueError:
        ekey = ctx.create_key(csp.CRYPT_EXPORTABLE, csp.AT_KEYEXCHANGE)

    assert ekey, 'NULL exchange key'
    return True


def remove_key(cont, local=True):
    '''
    Удаление контейнера

    :cont: Имя контейнера
    :local: Если True, контейнер создается в локальном хранилище по умолчанию
    :returns: True, если операция успешна

    '''
    provider = b"Crypto-Pro HSM CSP" if not local else None
    csp.Crypt.remove(bytes(cont), csp.PROV_GOST_2001_DH, provider)
    return True


def create_request(cont, params, local=True):
    """Создание запроса на сертификат

    :cont: Имя контейнера
    :params: Параметры запроса в виде словаря следующего вида:
        {
        'Attributes' : список пар [('OID', 'значение'), ...],
        'CertificatePolicies' : список вида [(OID, [(квалификатор, значение), ...]), ... ]
            OID - идент-р политики
            квалификатор - OID
            значение - произвольная байтовая строка
        'ValidFrom' : Дата начала действия (объект `datetime`),
        'ValidTo' : Дата окончания действия (объект `datetime`),
        'EKU' : список OIDов,
        'SubjectAltName' : список вида [(тип, значение), (тип, значение), ]
            где значение в зависимости от типа:
                'otherName' : ('OID', 'байтовая строка')
                'ediPartyName' : ('строка', 'строка') или 'строка'
                'x400Address' : 'байтовая строка'
                'directoryName' : [('OID', 'строка'), ...]
                'dNSName' : строка
                'uniformResourceIdentifier' : строка
                'iPAddress' : строка
                'registeredID' : строка
        'KeyUsage' : список строк ['digitalSignature', 'nonRepudiation', ...]
        'RawExtensions' : список троек [('OID', 'байтовая строка', bool(CriticalFlag)), ...]
            предназначен для добавления в запрос произвольных расширений,
            закодированных в DER-кодировку внешними средставми
        }
    :local: Если True, работа идет с локальным хранилищем
    :returns: байтовая строка с запросом в DER-кодировке

    """

    provider = b"Crypto-Pro HSM CSP" if not local else None
    ctx = csp.Crypt(bytes(cont), csp.PROV_GOST_2001_DH, 0, provider)
    req = csp.CertRequest(ctx, )
    set_q_defaults(params)
    req.set_subject(Attributes(params.get('Attributes', [])).encode())
    validity = CertValidity(params.get('ValidFrom', datetime.now()),
                            params.get('ValidTo', datetime.now() + timedelta(days=365)))
    eku = EKU(params.get('EKU', []))
    usage = KeyUsage(params.get('KeyUsage', []))
    all_exts = [usage, eku]
    altname = params.get('SubjectAltName', [])
    if len(altname):
        all_exts.append(SubjectAltName(altname))
    pols = params.get('CertificatePolicies', [])
    if len(pols):
        all_exts.append(CertificatePolicies(pols))
    for (oid, data, crit) in params.get('RawExtensions', []):
        all_exts.append(CertExtension(bytes(oid), data, bool(crit)))
    ext_attr = CertExtensions(all_exts)
    validity.add_to(req)
    ext_attr.add_to(req)
    return req.get_data()


def bind_cert_to_key(cont, cert, local=True):
    """Привязка сертификата к закрытому ключу в контейнере

    :cont: Имя контейнера
    :cert: Сертификат в байтовой строке
    :local: Если True, работа идет с локальным хранилищем
    :returns: отпечаток сертификата в виде строки

    """
    provider = b"Crypto-Pro HSM CSP" if not local else None
    cert = autopem(cert)
    ctx = csp.Crypt(bytes(cont), csp.PROV_GOST_2001_DH, 0, provider)
    newc = csp.Cert(cert)
    newc.bind(ctx)
    cs = csp.CertStore(ctx, b"MY")
    cs.add_cert(newc)
    return hexlify(newc.thumbprint())


def get_certificate(thumb):
    """Поиск сертификатов по отпечатку

    :thumb: отпечаток, возвращенный функцией `bind_cert_to_key`
    :returns: сертификат в байтовой строке

    """
    cs = csp.CertStore(None, b"MY")
    res = list(cs.find_by_thumb(unhexlify(thumb)))
    assert len(res), 'Cert not found'
    cert = res[0]
    return cert.extract()


def sign(thumb, data, include_data):
    """Подписывание данных сертификатом

    :thumb: отпечаток сертификата, которым будем подписывать
    :data: бинарные данные, байтовая строка
    :include_data: булев флаг, если True -- данные прицепляются вместе с подписью
    :returns: данные и/или подпись в виде байтовой строки

    """
    cs = csp.CertStore(None, b"MY")
    store_lst = list(cs.find_by_thumb(unhexlify(thumb)))
    assert len(store_lst), 'Unable to find signing cert in system store'
    signcert = store_lst[0]
    mess = csp.CryptMsg()
    sign_data = mess.sign_data(data, signcert, not(include_data))
    return sign_data


def sign_and_encrypt(thumb, certs, data):
    """Подписывание данных сертификатом

    :thumb: отпечаток сертификата, которым будем подписывать
    :certs: список сертификатов получателей
    :data: байтовая строка с данными
    :returns: данные и подпись, зашифрованные и закодированные в байтовую строку

    """
    certs = [autopem(c) for c in certs]
    cs = csp.CertStore(None, b"MY")
    store_lst = list(cs.find_by_thumb(unhexlify(thumb)))
    assert len(store_lst), 'Unable to find signing cert in system store'
    signcert = store_lst[0]
    mess = csp.CryptMsg()
    for c in certs:
        cert = csp.Cert(c)
        mess.add_recipient(cert)
    sign_data = mess.sign_data(data, signcert)
    encrypted = mess.encrypt_data(sign_data)
    return encrypted


def check_signature(cert, sig, data):
    """Проверка подписи под данными

    :cert: сертификат в байтовой строке
    :data: бинарные данные в байтовой строке
    :sig: данные подписи в байтовой строке
    :local: Если True, работа идет с локальным хранилищем
    :returns: True или False

    """
    sign = csp.Signature(sig)
    cert = autopem(cert)
    cert = csp.Cert(cert)
    icert = csp.CertInfo(cert)
    cissuer = icert.issuer()
    cserial = icert.serial()
    for i in range(sign.num_signers()):
        isign = csp.CertInfo(sign, i)
        if (cissuer == isign.issuer() and
                cserial == isign.serial()):
            return sign.verify_data(data, i)
    return False


def encrypt(certs, data):
    """Шифрование данных на сертификатах получателей

    :certs: список сертификатов в байтовых строках
    :data: данные в байтовой строке
    :returns: шифрованные данные в байтовой строке

    """
    bin_data = data
    certs = [autopem(c) for c in certs]
    msg = csp.CryptMsg()
    for c in certs:
        cert = csp.Cert(c)
        msg.add_recipient(cert)
    encrypted = msg.encrypt_data(bin_data)
    return encrypted


def decrypt(data, thumb):
    """Дешифрование данных из сообщения

    :thumb: отпечаток сертификата для расшифровки
    :data: данные в байтовой строке
    :returns: шифрованные данные в байтовой строке

    """
    cs = csp.CertStore(None, b"MY")
    certs = list(cs.find_by_thumb(unhexlify(thumb)))
    assert len(certs), 'Certificate for thumbprint not found'
    decrcs = csp.CertStore()
    decrcs.add_cert(certs[0])
    bin_data = data
    msg = csp.CryptMsg(bin_data)
    decrypted = msg.decrypt(decrcs)
    return decrypted


def pkcs7_info(data):
    """Информация о сообщении в формате PKCS7

    :data: данные в байтовой строке
    :returns: словарь с информацией следующего вида:
    {
        'Content': '....', # байтовая строка
        'Certificates': [сертификат, сертификат, ...], # байтовые строки
        'SignerInfos': [ { 'SerialNumber': 'строка', 'Issuer': [(OID, 'строка'), ... ] }, ... ],
        'ContentType': 'signedData' # один из ('data', 'signedData',
                                    #   'envelopedData', 'signedAndEnvelopedData', 'digestedData',
                                    #   'encryptedData')
        'RecipientInfos': [ { 'SerialNumber': 'строка', 'Issuer': [(OID, строка), ...] }, ... ],
    }


    """
    msg = csp.CryptMsg(data)
    res = PKCS7Msg(data).abstract()
    res['Content'] = msg.get_data()
    res['Certificates'] = list(x.extract() for x in csp.CertStore(msg))
    return res


def cert_info(cert):
    """Информация о сертификате

    :cert: сертификат в base64
    :returns: словарь с информацией следующего вида:
    {
        'Version' : целое число,
        'ValidFrom' : ДатаНачала (тип datetime),
        'ValidTo' : ДатаОкончания (тип datetime),
        'Issuer': [(OID, строка), ...],
        'UseToSign': булев флаг,
        'UseToEncrypt' : булев флаг,
        'Thumbprint': строка,
        'SerialNumber': СерийныйНомер,
        'Subject': [(OID, строка), ...],
        'Extensions': [OID, OID, ...]
    }

    """
    cert = autopem(cert)
    infoasn = CertificateInfo(cert)
    cert = csp.Cert(cert)
    info = csp.CertInfo(cert)
    res = dict(
        Version=info.version(),
        ValidFrom=filetime_from_dec(info.not_before()),
        ValidTo=filetime_from_dec(info.not_after()),
        Issuer=Attributes.load(info.issuer(False)).decode(),
        Thumbprint=hexlify(cert.thumbprint()),
        UseToSign=bool(info.usage() & csp.CERT_DIGITAL_SIGNATURE_KEY_USAGE),
        UseToEncrypt=bool(info.usage() & csp.CERT_DATA_ENCIPHERMENT_KEY_USAGE),
        SerialNumber=':'.join(hex(ord(x))[2:] for x in reversed(info.serial())),
        Subject=Attributes.load(info.name(False)).decode(),
        Extensions=infoasn.EKU(),
    )
    return res
