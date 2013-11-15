import os


class Recipe(object):
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.bin_dir = self.buildout['buildout']['bin-directory']
        self.options.setdefault('admin-name', 'admin')

    def install(self):
        recipe_egg_path = os.path.dirname(__file__)[:-len(
            self.options['recipe'])].replace("\\", "/")
        template_file = os.path.join(os.path.dirname(__file__),
                                     'script.py_tmpl').replace("\\", "/")
        template = open(template_file, 'r').read()
        template = template % dict(admin_name=self.options['admin-name'],
                                   recipe_egg_path=recipe_egg_path)

        open(self.bin_dir + '/ploneUpdater', 'w+').write(template)
        return tuple()

    def update(self):
        self.install()
