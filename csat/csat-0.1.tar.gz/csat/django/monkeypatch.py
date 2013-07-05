def patch_assets_finder():
    """
    Monkey patch django_assets in order to retrieve assets
    from a custom directory ('assets', in this case) instead
    of the static files directory. This prevents assets like
    less files to be exposed by the staticfiles framework.
    """

    from django_assets import env
    from django.contrib.staticfiles import finders, storage

    class AppDirectoriesFinder(finders.AppDirectoriesFinder):
        """
        Emulate the parts used by django_assets of the interface of the
        `django.contrib.staticfiles.finders` module and implement a generic
        `django.contrib.staticfiles.AppDirectoriesFinder` class.
        """
        def __init__(self, directory):
            class _Storage(storage.AppStaticStorage):
                source_dir = directory
            self.storage_class = _Storage
            super(AppDirectoriesFinder, self).__init__()

        def get_finders(self):
            yield self

        def find(self, path):
            return super(AppDirectoriesFinder, self).find(path) or None

    env.DjangoResolver.use_staticfiles = True
    env.finders = AppDirectoriesFinder('assets')


def patch_render_shortcut():
    """
    Monkey patch the django render shortcut in order to automatically
    set the current_app from the request if none is provided.
    """
    from django import shortcuts
    from django.template import loader

    _old_render = shortcuts.render
    _old_render_to_string = loader.render_to_string

    def _render(request, *args, **kwargs):
        if 'current_app' not in kwargs:
            try:
                kwargs['current_app'] = request.resolver_match.namespace
            except AttributeError as e:
                print e
        return _old_render(request, *args, **kwargs)

    def _render_to_string(request, *args, **kwargs):
        if 'current_app' not in kwargs:
            try:
                kwargs['current_app'] = request.resolver_match.namespace
            except AttributeError as e:
                print e
                raise
        return _old_render_to_string(request, *args, **kwargs)

    shortcuts.render = _render
    #loader.render_to_string = _render_to_string


def patch():
    """
    Use the following function to apply the monkey patches
    """
    for k, v in globals().iteritems():
        if k.startswith('patch_') and callable(v):
            try:
                v()
                print(u'Applied monkey patch {}'.format(k))
            except Exception as e:
                print(u'Failed to apply monkey patch {}'.format(k))
                print(u'{}: {}'.format(type(e), unicode(e)))
                import traceback
                traceback.print_exc()
                raise
