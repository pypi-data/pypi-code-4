from django.conf import settings

from skypehub.utils import get_skype, get_skype_hook_options


def skype_required(view):
    def _inner(request, *args, **kwargs):
        hook_options = get_skype_hook_options()
        skype = get_skype(**hook_options)
        return view(request, skype, *args, **kwargs)
    return _inner
