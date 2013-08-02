def _menu_item(text, link, text_params=None, perms=None, need_auth=None, link_args=None, link_kwargs=None, need_guest=None, no_reverse=False, sub_menu=None, highlights=None):
    d = {
        'text': text,
        'link': link,
        'text_params': text_params,
        'need_auth': need_auth,
        'need_guest': need_guest,
        'perms': perms,

        'link_args': link_args,
        'link_kwargs': link_kwargs,
        'no_reverse': no_reverse,
        'highlight-names': highlights
    }

    if sub_menu is not None:
        d['sub_menu'] = sub_menu

    return d


def menu_item(text, link, text_params=None, perms=None, need_auth=None, link_args=None, link_kwargs=None, need_guest=None, no_reverse=False, sub_menu=None, **kwargs):
    return _menu_item(text, link, text_params=text_params, perms=perms, need_auth=need_auth, link_args=link_args, link_kwargs=link_kwargs, need_guest=need_guest, no_reverse=no_reverse,
                      sub_menu=sub_menu, **kwargs)


def user_menu_item(text, link, text_params=None, perms=None, link_args=None, link_kwargs=None, no_reverse=False, sub_menu=None, **kwargs):
    return _menu_item(text, link, text_params=text_params, perms=perms, need_auth=True, link_args=link_args, link_kwargs=link_kwargs, need_guest=False, no_reverse=no_reverse,
                      sub_menu=sub_menu, **kwargs)


def guest_item(text, link, text_params=None, link_args=None, link_kwargs=None, no_reverse=False, sub_menu=None, **kwargs):
    return _menu_item(text, link, text_params=text_params, link_args=link_args, link_kwargs=link_kwargs, need_guest=True, no_reverse=no_reverse, sub_menu=sub_menu, **kwargs)


#
#   Sub Menu Items
#
def item_with_sub_menu(text, text_params=None, link="#", perms=None, need_auth=None, need_guest=None, sub_menu=None, **kwargs):
    return _menu_item(text, text_params=text_params, link=link, perms=perms, need_auth=need_auth, need_guest=need_guest, sub_menu=sub_menu, **kwargs)


def guest_item_with_sub_menu(text, text_params=None, link="#", sub_menu=None, **kwargs):
    return _menu_item(text, text_params=text_params, link=link, need_auth=False, need_guest=True, sub_menu=sub_menu, **kwargs)


def user_item_with_sub_menu(text, text_params=None, link="#", perms=None, sub_menu=None, **kwargs):
    return _menu_item(text, text_params=text_params, link=link, perms=perms, need_auth=True, need_guest=False, sub_menu=sub_menu, **kwargs)
