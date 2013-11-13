import os
import pipes
from fabric.api import local, settings, hide

def prepare_folder(folder):
    """
    Create folder if not exists and set up owner properly.
    """
    cmd_prefix = ""

    with settings(warn_only=True):
        if local("test -d %s" % folder).failed:
            local("%s mkdir -p %s" % (cmd_prefix, folder))


def prepare_virtual_env(virtualenv, python):
    with settings(warn_only=True):
        if local("test -d %s" % virtualenv).failed:
            local("virtualenv --no-site-packages --python=%s %s" % (python, virtualenv))
        elif local("test -d %s" % os.path.join(virtualenv, "lib", python)).failed:
            local("sudo rm -rf %s" % virtualenv)
            local("virtualenv --no-site-packages --python=%s %s" % (python, virtualenv))


def local_sed(filename, before, after, limit='', flags=''):
    """
    Run a search-and-replace on ``filename`` with given regex patterns.

    Equivalent to ``sed -i -r -e "/<limit>/ s/<before>/<after>/<flags>g
    <filename>"``.

    For convenience, ``before`` and ``after`` will automatically escape forward
    slashes, single quotes and parentheses for you, so you don't need to
    specify e.g.  ``http:\/\/foo\.com``, instead just using ``http://foo\.com``
    is fine.

    `sed` will pass ``shell=False`` to `run`/`sudo`, in order to avoid problems
    with many nested levels of quotes and backslashes.

    Other options may be specified with sed-compatible regex flags -- for
    example, to make the search and replace case insensitive, specify
    ``flags="i"``. The ``g`` flag is always specified regardless, so you do not
    need to remember to include it when overriding this parameter.

    .. versionadded:: 1.1
        The ``flags`` parameter.
    """
    # Characters to be escaped in both
    for char in "/'":
        before = before.replace(char, '\%s' % char)
        after = after.replace(char, '\%s' % char)
    # Characters to be escaped in replacement only (they're useful in regexen
    # in the 'before' part)
    for char in "()":
        after = after.replace(char, '\%s' % char)
    if limit:
        limit = '/%s/ ' % limit

    expr = "LC_ALL=C sed -i -r -e '%ss/%s/%s/%sg' %s"
    command = expr % (limit, before, after, flags, filename)
    return local(command)

def local_template(filename, destination, context=None, use_jinja=False,
    template_dir=None, backup=True, mirror_local_mode=False,
    mode=None):
    """
    Render and upload a template text file to a remote host.

    ``filename`` should be the path to a text file, which may contain `Python
    string interpolation formatting
    <http://docs.python.org/release/2.5.4/lib/typesseq-strings.html>`_ and will
    be rendered with the given context dictionary ``context`` (if given.)

    Alternately, if ``use_jinja`` is set to True and you have the Jinja2
    templating library available, Jinja will be used to render the template
    instead. Templates will be loaded from the invoking user's current working
    directory by default, or from ``template_dir`` if given.

    The resulting rendered file will be uploaded to the remote file path
    ``destination``.  If the destination file already exists, it will be
    renamed with a ``.bak`` extension unless ``backup=False`` is specified.

    By default, the file will be copied to ``destination`` as the logged-in
    user.

    The ``mirror_local_mode`` and ``mode`` kwargs are passed directly to an
    internal `~fabric.operations.put` call; please see its documentation for
    details on these two options.

    .. versionchanged:: 1.1
        Added the ``backup``, ``mirror_local_mode`` and ``mode`` kwargs.
    """
    # Normalize destination to be an actual filename, due to using StringIO
    with settings(hide('everything'), warn_only=True):
        if local('test -d %s' % destination).succeeded:
            sep = "" if destination.endswith('/') else "/"
            destination += sep + os.path.basename(filename)

    # Use mode kwarg to implement mirror_local_mode, again due to using
    # StringIO
    if mirror_local_mode and mode is None:
        mode = os.stat(filename).st_mode
        # To prevent put() from trying to do this
        # logic itself
        mirror_local_mode = False

    # Process template
    text = None
    if use_jinja:
        try:
            from jinja2 import Environment, FileSystemLoader, contextfunction, StrictUndefined

            loader = FileSystemLoader(template_dir or '.')
            jenv = Environment(loader=loader, undefined=StrictUndefined)
            jenv.filters["shquote"] = lambda s: pipes.quote(str(s))

            template = jenv.get_template(filename)

            # add debugging function to template
            @contextfunction
            def get_context(c):
                return c
            template.globals['context'] = get_context
            template.globals['callable'] = callable

            text = template.render(**context or {})
        except ImportError:
            import traceback
            tb = traceback.format_exc()
            abort(tb + "\nUnable to import Jinja2 -- see above.")
    else:
        with open(filename) as inputfile:
            text = inputfile.read()
        if context:
            text = text % context

    # Back up original file
    if backup and exists(destination):
        local("cp %s{,.bak}" % destination)

    # Upload the file.
    with open(destination, "w") as f:
        f.write(text)


def get_temp_path(name=None):
    """
    Create a temp folder, unique by name.
    """
    if name:
        dirpath = os.path.join("/", "tmp", "trebuchet", name)
        prepare_folder(dirpath)
    else:
        import tempfile
        dirpath = tempfile.mkdtemp()
    return dirpath
