import random
from sample_data_utils.storage import load_data
from sample_data_utils.text import rtext
from sample_data_utils.utils import memoize

GENDER_MALE = 'm'
GENDER_FEMALE = 'f'


@memoize
def _get_firstnames(language, gender):
    fn = load_data(language, "firstnames_%s.txt" % gender)
    return fn


@memoize
def _get_lastnames(language):
    fn = load_data(language, "lastnames.txt")
    return fn


@memoize
def _get_titles(languages=None):
    choices = []
    languages = languages or ['en']
    for lang in languages:
        fn = load_data(lang, "title.txt")
        choices.extend([line.split('/') for line in fn])
    return choices


def title(languages=None, genders=None):
    """
    returns a random title

    .. code-block:: python

        >>> d.title()
        u'Mrs.'
        >>> d.title(['es'])
        u'El Sr.'
        >>> d.title(None, [GENDER_FEMALE])
        u'Mrs.'

    :param languages: list of allowed languages. ['en'] if None
    :param genders: list of allowed genders. (GENDER_FEMALE, GENDER_MALE) if None
    """
    languages = languages or ['en']
    genders = genders or (GENDER_FEMALE, GENDER_MALE)

    choices = _get_titles(languages)
    gender = {'m':0, 'f':1}[random.choice(genders)]

    return random.choice(choices)[gender]


def gender():
    """
    randomly returns 'm' or 'f'
    """
    return random.choice((GENDER_FEMALE, GENDER_MALE))


def person(languages=None, genders=None):
    """
    returns a random tuple representing person information

    .. code-block:: python

        >>> d.person()
        (u'Derren', u'Powell', 'm')
        >>> d.person(genders=['f'])
        (u'Marge', u'Rodriguez', u'Mrs.', 'f')
        >>> d.person(['es'],['m'])
        (u'Jacinto', u'Delgado', u'El Sr.', 'm')

    :param language:
    :param genders:
    """
    languages = languages or ['en']
    genders = genders or (GENDER_FEMALE, GENDER_MALE)


    lang = random.choice(languages)
    g = random.choice(genders)
    t = title([lang], [g])
    return first_name([lang], [g]), last_name([lang]), t, g


def name():
    return rtext(30, 10).capitalize()


def fullname():
    return "%s %s" % (name(), name())


def first_name(languages=None, genders=None):
    """
        return a random first name
    :return:

    >>> from mock import patch
    >>> with patch('%s._get_firstnamess' % __name__, lambda *args: ['aaa']):
    ...     first_name()
    'Aaa'
    """
    choices = []
    languages = languages or ['en']
    genders = genders or [GENDER_MALE, GENDER_FEMALE]
    for lang in languages:
        for gender in genders:
            samples = _get_firstnames(lang, gender)
            choices.extend(samples)
    return random.choice(choices).title()


def last_name(languages=None):
    """
        return a random last name

    >>> from mock import patch
    >>> with patch('%s._get_lastnames' % __name__, lambda *args: ['aaa']):
    ...     last_name()
    'Aaa'
    >>> with patch('%s.get_lastnames' % __name__, lambda lang: ['%s_lastname'% lang]):
    ...     last_name(['it'])
    'It_Lastname'
    """
    choices = []
    languages = languages or ['en']
    for lang in languages:
        samples = _get_lastnames(lang)
        choices.extend(samples)
    return random.choice(choices).title()
