# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from paste.script.templates import var
import datetime
import os
import os.path
import paste.script.templates
import paste.util.template
import pkginfo
import shutil
import subprocess


class Skeleton(paste.script.templates.Template):

    summary = (
        'Python package with buildout, conforming to conventions at gocept')

    _template_dir = 'skeleton'

    template_renderer = staticmethod(
        paste.util.template.paste_script_template_renderer)

    vars = [
        var("description", "One-line description of the package"),
        var("keywords", "Space-separated keywords/tags"),
    ]

    def underline_double(self, text):
        return '=' * len(text)

    def pre(self, command, output_dir, vars):
        namespace, package = vars['egg'].split('.')
        gocept_package = pkginfo.Installed('gocept.package')
        vars.update(
            namespace=namespace,
            package=package,
            year=datetime.date.today().year,
            underline_double=self.underline_double,
            gocept_package_version=gocept_package.version,
            )

    def post(self, command, output_dir, vars):
        os.rename(os.path.join(output_dir, 'hgignore'),
                  os.path.join(output_dir, '.hgignore'))
        subprocess.call(['hg', 'init', output_dir])
        shutil.move(os.path.join(output_dir, 'hgrc'),
                    os.path.join(output_dir, '.hg'))

        os.rename(os.path.join(output_dir, 'coveragerc'),
                  os.path.join(output_dir, '.coveragerc'))
