
from docutils import nodes, utils
from docutils.parsers.rst.roles import register_canonical_role, set_classes

def card_reference_role(role, rawtext, text, lineno, inliner,
                       options={}, content=[]):
    text = text.strip()
    try:
        wikiid, rest = text.split(u':', 1)
    except:
        wikiid, rest = text, text
    context = inliner.document.settings.context
    ref = context._cw.build_url('card/' + wikiid)
    rset = context._cw.execute('Card C WHERE C wikiid %(w)s', {'w': wikiid})
    set_classes(options)
    if not rset:
        options['classes'] = ['doesnotexist']
    else:
        options.pop('classes', None)
    return [nodes.reference(rawtext, utils.unescape(rest), refuri=ref,
                            **options)], []

register_canonical_role('card', card_reference_role)
