import sh

from thejoke import punchline

def tell():
    out = sh.echo(punchline())
    print out
    out = sh.echo(sh.__version__)
    print out
