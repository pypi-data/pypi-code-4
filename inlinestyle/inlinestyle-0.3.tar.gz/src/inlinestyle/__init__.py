from bs4 import BeautifulSoup as Soup
from soupselect import select
import cssutils
import string
import re


class InlineStyler(object):
    def __init__(self, html_string, parser="html.parser"):
        self._original_html = html_string
        self._soup = Soup(self._original_html, parser)
        self._media_queries = u''

    def _strip_styles(self):
        style_blocks = self._soup.find_all('style')
        css_list = []
        for style_block in style_blocks:
            if style_block.contents:
                css_list.append(style_block.contents[0])
            style_block.extract()
        return css_list

    def _selector_specificity_score(self, selector, is_inline=False):
        '''
            Gives a CSS selector string a specificity score as detailed by the W3C:
            http://www.w3.org/TR/CSS2/cascade.html#specificity

            More about CSS order of precedence:
            http://www.alternategateways.com/tutorials/css/css-101/part-four-the-css-order-of-precedence

            IMPORTANT: this function assumes `selector` is not a comma-delimited
            list of selectors.

            TODO: support child selector >
            TODO: support adjacent sibling selector +
        '''
        if is_inline:
            return "1-0-0-0"

        ids = 0
        attrs = 0
        elements = 0

        # count ids
        ids += selector.count("#")

        # count attributes and pseudo-classes
        attrs += selector.count(".")
        attrs += selector.count("[")

        # count elements and pseudo-elements
        elements += selector.count(":")
        for el in selector.split(" "):
            if re.match(r'^[A-Za-z]+', el):
                elements += 1

        return "0-%s-%s-%s" % (ids, attrs, elements)

    def _load_sheet(self, css_list):
        parser = cssutils.CSSParser()
        self._sheet = parser.parseString(u''.join(css_list))
        return self._sheet

    def _pre_process_inline_styles(self):
        '''
            Put specificity scores on any styles already in `style` attributes
            so they get top priority.
        '''
        for tag in self._soup.find_all(lambda t: t.has_key('style')):
            styles = tag['style'].split(';')
            score = self._selector_specificity_score('', is_inline=True)
            styles = [u"%s(spec:%s)" % (s, score) for s in styles]
            tag['style'] = ';'.join(styles)

    def _sort_inline_properties(self):
        '''
            Sorts inline rules in `style` attributes by the specificity of
            their original selector.
        '''
        for tag in self._soup.find_all(lambda t: t.has_key('style')):
            tag_styles = tag['style'].split(';')

            clean_styles = []
            for i, style in enumerate(tag_styles):
                # break out specificity score
                scored_re = re.match(r'^(.*?)\(spec\:(.*?)\)$', style)
                clean_style = scored_re.group(1)
                score = "%s-%s" % (scored_re.group(2), str(i).zfill(3))
                clean_styles.append((score, clean_style, ))

            # sort styles by specificity score and rejoin
            sorted_styles = sorted(clean_styles)
            final_styles = filter(None, [t[1] for t in sorted_styles])
            tag['style'] = ';'.join(final_styles)

    def _apply_rules(self):
        '''
            INLINE ALL THE THINGS
        '''
        self._pre_process_inline_styles()

        for item in self._sheet.cssRules:
            if item.type == item.STYLE_RULE:
                selectors = item.selectorText
                for selector in selectors.split(','):
                    selector_score = self._selector_specificity_score(selector)
                    items = select(self._soup, selector)

                    for element in items:
                        styles = item.style.cssText.splitlines()
                        new_styles = [style.replace(';', u'').replace(
                                        '"', u"'") for style in styles]

                        all_styles = element.get('style', u'')
                        if isinstance(all_styles, unicode):
                            all_styles = all_styles.split(';')

                        # add specificity score to properties for later sorting
                        scored_styles = []
                        for s in new_styles:
                            scored_styles.append(u"%s(spec:%s)" % (s,
                                selector_score))

                        all_styles.extend(scored_styles)
                        all_styles = filter(None, all_styles)

                        element['style'] = u';'.join(all_styles)
            elif item.type == item.MEDIA_RULE:
                self._media_queries += u'\n%s' % item.cssText

        self._sort_inline_properties()

        return self._soup

    def convert(self, remove_class=False, remove_id=False):
        css_list = self._strip_styles()
        self._load_sheet(css_list)
        html = self._apply_rules()

        if remove_class:
            for element in html.find_all(lambda tag: tag.has_key('class')):
                del element['class']

        if remove_id:
            for element in html.find_all(lambda tag: tag.has_key('id')):
                del element['id']

        html = unicode(html)
        if self._media_queries:
            html = '<style>%s</style>%s' % (self._media_queries, html)

        return html


def remove_whitepace(input_string):
    filtered_string = filter(lambda x: x not in string.whitespace,
            input_string)
    return filtered_string
