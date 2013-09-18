import tidylib
tidylib.BASE_OPTIONS['preserve-entities'] = True

from BeautifulSoup import BeautifulSoup, Comment, Tag

from pml.constants import COLORS


class InvalidColorException(Exception):
    pass


def resolve_color(color):
    """
    Resolves a provided simple color, i.e. 'red' to its PML equivalent,
    i.e. MiRed
    @param color string: simple color
    @return string: resolved PML color or InvalidColorException if color
        could not be resolved, or None if provided color is None.
    """
    if color:
        if color.lower() not in COLORS:
            raise InvalidColorException()
    else:
        return None

    return 'Mi%s' % color.title()


def gen_context(color):
    """
    Generates a context containing base module attributes
    @param color string: module background color
    @return dict: context dictionary
    """
    return {
        'color': resolve_color(color),
    }


def html_to_text(html):
    """
    Evaluates provided HTML and converts result to PML for TEXT containers.
    @param html string: html to convert
    @param Context context: context to be used for html evaluation
    @return string: evaluated HTML converted to TEXT appropriate PML
    """

    def fake_ul(soup, tag):
        # Fake UL elements by inserting a p with a prefixed dash for
        # each LI
        p_tag = Tag(soup, 'p')
        insertables = []
        for li in tag.findAll('li'):
            insertables.append('- %s' % (li.text,))
            insertables.append(Tag(soup, 'br'))

        for index, element in enumerate(insertables):
            p_tag.insert(index, element)
        return p_tag

    def convert_anchor(soup, tag):
        link_tag = Tag(soup, 'LINK')
        try:
            link_tag['href'] = tag['href']
        except KeyError:
            pass

        link_tag.insert(0, tag.text)
        return link_tag

    def convert_font(soup, tag):
        try:
            color_tag = Tag(soup, 'color')
            color_tag['value'] = tag['color']
            color_tag.insert(0, tag.text)
            return color_tag
        except KeyError:
            return tag.text

    html = sanitize_html(html)
    soup = BeautifulSoup(html)
    soup = swap_tags(soup, [
        ('a', convert_anchor),
        ('ul', fake_ul),
        ('font', convert_font)
    ])

    return soup.renderContents().decode('utf8')


def remove_comments(soup):
    # remove all comments from the HTML
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    return soup


def swap_tags(soup, tags):
    for element, replacer in tags:
        for tag in soup.findAll(element):
            if callable(replacer):
                replacement_tag = replacer(soup, tag)
            else:
                if element == replacer:
                    continue
                replacement_tag = Tag(soup, replacer)
                replacement_tag.insert(0, tag.text)
            tag.replaceWith(replacement_tag)
    return soup


def sanitize_html(value):
    # FIXME: 'None' should never be saved as text
    if value is None:
        return ''

    # allowed tags for a Vodafone Live <CONTAINER type="data" />
    # this doubles up as a translation table. CKEditor does new-ish
    # HTML than Vodafone Live will accept. We have to translate 'em' back
    # to 'i', and 'strong' back to 'b'.
    #
    # NOTE: Order is important since <strong>'s can be inside <p>'s.
    tags = (
        ('em', 'i'),  # when creating them in the editor they're EMs
        ('strong', 'b'),
        ('i', 'i'),  # when loading them as I's the editor leaves them
        ('b', 'b'),  # we keep them here to prevent them from being removed
        ('u', 'u'),
        ('br', 'br'),
        ('p', 'p'),
        ('li', 'li'),
        ('ul', 'ul'),
        ('small', 'small'),

        # FIXME:    Because of how this is implemented this method might
        #           be called twice because our crazy template-in-a-template
        #           setup. If that's the case we'll potentially get HTML
        #           on the first round and PML on the second round.
        #           We unfortunately need to deal with both.
        ('a', 'a'),         # this allows `html_to_text` to replace them with LINKs
        ('font', 'font'),   # this allows `html_to_text` to replace them with COLORs
    )
    valid_tags = [tag for tag, replacement_tag in tags]
    soup = BeautifulSoup(value)
    soup = remove_comments(soup)

    # hide all tags that aren't in the allowed list, but keep
    # their contents
    for tag in soup.findAll(True):
        # Vodafone Live allows for no tag attributes
        # tag.attrs = []
        if tag.name not in valid_tags:
            tag.hidden = True

    # replace tags with Vlive equivelants
    soup = swap_tags(soup, tags)

    xml = soup.renderContents().decode('utf8')
    fragment, errors = tidylib.tidy_fragment(xml, {
        'char-encoding': 'utf8'
    })

    return fragment \
            .replace('&nbsp;', ' ') \
            .replace('&rsquo;', '\'') \
            .replace('&lsquo;', '\'') \
            .replace('&quot;', '"') \
            .replace('&ldquo;', '"') \
            .replace('&rdquo;', '"') \
            .replace('&ndash;', "-")\
            .replace('&copy;', "&#169;")\
            .replace('&hellip;', "...")
