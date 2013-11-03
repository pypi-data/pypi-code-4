#!/usr/bin/env python

import subprocess
import sys
import os
import re
import argparse
import requests
from uuid import uuid4


def check_gpg():
    try:
        subprocess.check_call(['gpg', '--version'])
    except OSError:
        raise Exception("gpg not found.")


def otp_prompt(octopus_url):
    """
    Do not use stdin, it is reserved for secret contents.
    """
    tty_fd = os.open('/dev/tty', os.O_RDWR|os.O_NOCTTY)
    tty = os.fdopen(tty_fd, 'w+')
    print >> tty, "Octopus URL: %s" % octopus_url
    if not octopus_url.startswith('https'):
        print >> tty, "WARNING: Octopus URL is not secure."
    tty.write("YubiKey OTP: ")
    tty.flush()
    return tty.readline().strip()


def hash(args):
    """
    prompt for OTP
    get and return digest from Octopus
    """
    octopus_url = args.octopus_url
    if octopus_url is None:
        octopus_url = os.environ['OCTOPUS_URL']

    otp = args.otp
    if otp is None:
        otp = otp_prompt(octopus_url)

    response = requests.get(
        octopus_url,
        params={'otp': otp, 'payload': args.payload})

    if response.status_code == 200:
        digest = response.text.strip()
        if len(digest) != 64 or not digest.isalnum():
            raise Exception("Bad response from Octopus: %s" % digest)
        print digest
    elif response.status_code in (401, 500):
        print >> sys.stderr, "Octopus error: %s" % response.text
        sys.exit(1)
    else:
        raise Exception(
            "Octopus returned %s: %s" % (response.status_code, response.text))



def get_octopus_digest_fd(payload, octopus_url):
    digest = subprocess.check_output(
        [
            sys.argv[0],
            'hash',
            '--octopus-url', octopus_url,
            payload,
        ])
    r_fd, w_fd = os.pipe()
    os.write(w_fd, digest + '\n')
    os.close(w_fd)
    return r_fd


def get_piped_secret_fd():
    piped_secret = sys.stdin.read()
    r_fd, w_fd = os.pipe()
    os.write(w_fd, piped_secret)
    os.close(w_fd)
    return r_fd


def put(args):
    octopus_url = args.octopus_url
    if octopus_url is None:
        octopus_url = os.environ['OCTOPUS_URL']

    keyid = os.environ['PEARPASS_KEYID']

    # If input is piped in, block on it.
    # Prevents otp prompt from interfering with possible password prompts
    # from parent process, like gpg.
    secret_fd = None
    if not sys.stdin.isatty():
        secret_fd = get_piped_secret_fd()

    check_gpg()

    pearpass_id = uuid4().hex
    digest_fd = get_octopus_digest_fd(pearpass_id, octopus_url)

    gpg_args = [
        'gpg',
        '--encrypt',
        '--symmetric',
        '--recipient', keyid,
        '--comment', 'pearpass_id=%s' % pearpass_id,
        '--comment', 'octopus_url=%s' % octopus_url,
        '--comment', 'pearpass_protocol_version=1',
        '--cipher-algo', 'AES',
        '--s2k-mode', '3',
        '--s2k-cipher-algo', 'AES',
        '--s2k-digest-algo', 'SHA256',
        '--compress-algo', 'uncompressed',
        '--passphrase-fd', str(digest_fd),
        '--trust-model', 'always',
        '--armor',
        '--output', args.outfile,
    ]

    gpg_stdin = None
    if secret_fd is not None:
        gpg_stdin = os.fdopen(secret_fd)

    subprocess.call(gpg_args, stdin=gpg_stdin)
    os.close(digest_fd)


def parse_comments(file, fields):
    _re = re.compile(
        r'Comment: (%s)=(.*)' % '|'.join(map(re.escape, fields)))
    matches = {}
    for line in file:
        match = _re.match(line)
        if match:
            matches[match.group(1)] = match.group(2)
    return matches


def get(args):
    check_gpg()

    matches = parse_comments(
        args.infile, ['pearpass_id', 'octopus_url'])
    args.infile.seek(0)
    pearpass_id = matches['pearpass_id']
    octopus_url = matches['octopus_url']
    digest_fd = get_octopus_digest_fd(pearpass_id, octopus_url)

    gpg_args = [
        'gpg',
        '--decrypt',
        '--keyring', os.devnull,
        '--no-default-keyring',
        '--passphrase-fd', str(digest_fd),
    ]

    subprocess.call(gpg_args, stdin=args.infile)
    os.close(digest_fd)


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Scripts for managing secrets with Octopus and GnuPG.")

subparsers = parser.add_subparsers(title="commands")

parser_put = subparsers.add_parser(
    'put', help="encrypt and save a new secret")
parser_put.add_argument('-o', '--octopus-url')
parser_put.add_argument('outfile', help="where to save encrypted output")
parser_put.set_defaults(func=put)

parser_get = subparsers.add_parser( 'get', help="decrypt a secret")
parser_get.add_argument(
    'infile', type=argparse.FileType('r'), help="Pearpass-encrypted input file")
parser_get.set_defaults(func=get)

parser_hash = subparsers.add_parser('hash', help="get a hash from Octopus")
parser_hash.add_argument('-o', '--octopus-url')
parser_hash.add_argument('payload')
parser_hash.add_argument('otp', nargs='?')
parser_hash.set_defaults(func=hash)

args = parser.parse_args()
args.func(args)
