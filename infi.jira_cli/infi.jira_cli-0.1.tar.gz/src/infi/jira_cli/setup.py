"""setup-jish
writes jish.zsh

Usage:
    setup-jish dump <filepath>
    setup-jish unattended


Options:
    dump                         dumps the zsh extension to file
"""

from os import path, environ, remove
from sys import stderr, argv
from infi.execute import execute_assert_success

JISH = """
jish () {
    eval $(jish=1 POSIXLY_CORRECT= jissue "$@")
}
"""


def _get_arguments(argv):
    from .__version__ import __version__
    from docopt import docopt
    from bunch import Bunch
    arguments = Bunch(docopt(__doc__, argv=argv, help=True, version=__version__))
    return arguments


def write_to(filepath):
    jissue_abspath = path.abspath(argv[0]).replace("setup-jish", "jissue")
    with open(filepath, "w") as fd:
        fd.write(JISH.replace("jissue", jissue_abspath if path.exists(jissue_abspath) else "jissue"))


def write_autocomplete_to(filepath):
    docopt_completion = path.abspath(argv[0]).replace("setup-jish", "docopt-completion")
    jissue_abspath = path.abspath(argv[0]).replace("setup-jish", "jissue")
    env = environ.copy()
    env['jish'] = 1
    execute_assert_success("jish=1 {} {} --manual-zsh".format(docopt_completion, jissue_abspath), shell=True)
    with open("_jissue") as fd:
        content = fd.read()
    remove("_jissue")
    with open(filepath, "w") as fd:
        fd.write(content.replace("jissue", "jish"))


def unattended_install():
    homedir = path.expanduser("~")
    yadr_zsh = path.join(homedir, ".yadr", "zsh")
    if path.exists(yadr_zsh):
        write_to(path.join(yadr_zsh, "jish.zsh"))
        write_autocomplete_to(path.join(yadr_zsh, "prezto", "modules", "completion", "external", "src", "_jish"))
        print >> stderr, "installed to yadr-zsh, reload your shell"
    else:
        print >> stderr, "installation failed, cannot deduce your shell setup"


def setup(argv):
    arguments = _get_arguments(argv)
    if arguments.dump:
        return write_to(arguments.get("<filepath>"))
    elif arguments.unattended:
        return unattended_install()


def main():
    return setup(argv[1:])
