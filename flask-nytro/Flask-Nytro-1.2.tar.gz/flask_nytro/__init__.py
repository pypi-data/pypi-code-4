import os, importlib
from flask import Blueprint as BP


class Blueprint(BP):

    def __init__(self, *args, **kwargs):
        if not kwargs.get('template_folder'):
            kwargs['template_folder'] = 'templates'
        if not kwargs.get('static_folder'):
            kwargs['static_folder'] = 'static'
        super(Blueprint, self).__init__(*args, **kwargs)

    @classmethod
    def attach_all(cls, app):
        cls.__load_by_convention(app)
        cls.__load_by_configuration(app)

    @classmethod
    def __load_by_convention(cls, app):
        blueprints_folder = app.config.get('BLUEPRINTS_FOLDER', 'blueprints')
        blueprints_path = os.path.join(app.root_path, blueprints_folder)

        if os.path.exists(blueprints_path):
            for blueprint_folder in os.listdir(blueprints_path):
                blueprint_folder_abspath = os.path.join(blueprints_path, blueprint_folder)

                if os.path.isdir(blueprint_folder_abspath):
                    blueprint = '%s.%s.%s' % (app.name, blueprints_folder, blueprint_folder)

                    views = cls.__import('%s.views' % blueprint)
                    app.register_blueprint(views.bp)

    @classmethod
    def __load_by_configuration(cls, app):
        blueprints = app.config.get('BLUEPRINTS')

        if blueprints:
            for module_name in blueprints:
                if app.name not in module_name:
                    module_name = '%s.%s' % (app.name, module_name)

                blueprint = cls.__import(module_name)

                for item in dir(blueprint):
                    if not item.startswith('_'):
                        attr = getattr(blueprint, item)

                        if issubclass(attr.__class__, BP):
                            app.register_blueprint(attr)
                            break

    @classmethod
    def __import(cls, module):
        err = u'Error while importing %s' % module
        try:
            print('importing: %s' % module)
            return importlib.import_module(module)
        except ImportError as e:
            raise ImportError('%s -> %s' % (err, e))
        except Exception as e:
            raise Exception('%s -> %s' % (err, e))

    def __repr__(self):
        return u'< %s in %s >' % (unicode(self.name), __name__)


