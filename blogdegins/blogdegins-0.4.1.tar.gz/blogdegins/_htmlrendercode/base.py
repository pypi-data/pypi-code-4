# -*- encoding: utf-8 -*-
import traceback
import os
from ginsfsm.gobj import GObj
from ginsfsm.gaplic import GAplic
from ghtml.c_ghtml import GHtml
from ginsfsm.gconfig import add_gconfig
from assets import get_assets_env
from mymako import get_mako_lookup
from webassets.exceptions import FilterError, BundleError

my_package = __package__.split('.')[0]

page_data = {
    'title': 'MyWeb',
    'base': 'http://www.myweb.com/',
    'metadata': {
        'application-name': 'blog',
        'description': '',
        'keywords': '',
    },
}


PAGE_GCONFIG = {
    'gaplic_namespace': [
        str, '', 0, None,
        'namespace of gaplic, to store callbacks.',
    ],
    'debug': [bool, False, 0, None, 'Debugging mode'],
    'output_path': [str, '', 0, None, "Output directory (current tag)."],
    'here': [str, '', 0, None, "Code path."],
}


class Base(GHtml):
    def __init__(self, fsm=None, gconfig=None):
        gconfig = add_gconfig(gconfig, PAGE_GCONFIG)
        super(Base, self).__init__(fsm=fsm, gconfig=gconfig)

    def render(self, **kw):
        htmlrendercode_path = os.path.join(
            self.config.here,
            my_package,
            'htmlrendercode')

        mako_lookup = get_mako_lookup(
            self.config.here,
            self.config.output_path
        )

        assets_env = get_assets_env(
            htmlrendercode_path,
            self.config.output_path,
            self.config.debug,
        )
        kw.update(**page_data)
        kw.update(assets_env=assets_env)
        try:
            rendered = super(Base, self).render(mako_lookup=mako_lookup, **kw)
        except FilterError:
            traceback.print_exc()
            print("<==== Please, check if webassets version is > 0.8dev !!!")
            exit(-1)
        except BundleError:
            traceback.print_exc()
            print(
                "<==== Please, check the symbolic links.\n"
                "You can recreate with 'blogdegins base <name>'"
                " or 'blogdegins widget <name>'\n"
                "In the sample supplied h5bp+jquery asset, you need to exec:\n"
                "   blogdegins page base\n"
                "   blogdegins page content\n"
                "   blogdegins widget boxlist\n\n"
            )
            exit(-1)

        return rendered


def get_base(here, output_path, debug):
    """ This is the only function being called from blogdegins.
        The rest is up to you.
        This function must return a class with a render method.
        The render method must return a string with the html code.
        :param here: path where blogdegins project resides.
        :param output_path: current output tag directory.
        :param debug: True if you want debug.
    """
    gaplic = GAplic(name='Root', all_unique_names=True)
    base = gaplic.create_gobj(
        None,
        Base,
        None,
        template='/%s/htmlrendercode/base.mako' % my_package,

        here=here,
        output_path=output_path,
        debug=debug,
        gaplic_namespace='mynamespace',
    )

    from content import create_content
    create_content(
        'content',
        base,
        gaplic_namespace=base.config.gaplic_namespace
    )
    return base
