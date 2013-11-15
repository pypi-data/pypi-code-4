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

        options = {}
        options['script'] = \
            '%s/uncsom/recipe/ploneupdater/ploneupdater.py' % recipe_egg_path
        options['bin-directory'] = self.bin_dir
        options['instance-script'] = 'instance'
        options['args'] = "--admin-user=%s" % self.options['admin-name']

        template = template % options

        open(self.bin_dir + '/ploneUpdater', 'w+').write(template)
        return tuple()

    def update(self):
        self.install()
