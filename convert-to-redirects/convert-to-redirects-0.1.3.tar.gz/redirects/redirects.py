"""Naval Fate.

Usage:
    redirects.py <type> <from> <to> [--remove-host=<host>]
    redirects.py (-h | --help)
    redirects.py --version

Options:
    <type>                      apache or nginx
    -h --help                   Show this screen.
    --version                   Show version.
    --remove-host=<host>        Substring host mane from urls

"""
from __future__ import print_function
from docopt import docopt
import os
import re

DIRNAME = os.getcwd()


def create_redirect(from_url, to_ulr, arguments, start, first, end):
    redirect_string = start + " "

    if arguments['--remove-host'] is not None:
        redirect_string += first
    else:
        redirect_string += 'http://'

    if arguments['--remove-host'] is not None:
        redirect_string += re.sub('(http:\/\/|\n|'+arguments['--remove-host'].replace('.', '\.')+'\/'+')', '', from_url)
    else:
        redirect_string += re.sub('\n', '', from_url)

    redirect_string += " "

    if arguments['--remove-host'] is not None:
        redirect_string += '/'+re.sub('(http:\/\/|\n|'+arguments['--remove-host'].replace('.', '\.')+'\/'+')', '', to_ulr)
    else:
        redirect_string += '/'+re.sub('\n', '', to_ulr)

    redirect_string += " " + end
    redirect_string = re.sub(r'(\?|\&)', r"\\\1", redirect_string)

    return redirect_string


def create_nginx_redirects(from_url, to_ulr, arguments):
    return create_redirect(from_url, to_ulr, arguments,
                           "rewrite", "^/", "permanent;")


def create_apache_redirects(from_url, to_ulr, arguments):
    return create_redirect(from_url, to_ulr, arguments,
                           "RewriteRule", "^", "[L,R=301]")


def save_out(out, arguments):
    out = "\n".join(out)
    print (out)


def console_command():
    arguments = docopt(__doc__, version='Convert to redirects 0.1.0')
    from_file_name = os.path.join(DIRNAME, arguments['<from>'])
    from_urls_list = open(from_file_name).readlines()

    to_file_name = os.path.join(DIRNAME, arguments['<to>'])
    to_urls_list = open(to_file_name).readlines()

    output = []

    for index, from_url in enumerate(from_urls_list):
        try:
            to_url = to_urls_list[index]
        except ValueError:
            print("can't find 'to' url")
            return False

        if arguments['<type>'] == 'apache':
            output.append(create_apache_redirects(from_url, to_url, arguments))
        elif arguments['<type>'] == 'nginx':
            output.append(create_nginx_redirects(from_url, to_url, arguments))
    save_out(output, arguments)


if __name__ == '__main__':
    console_command()
