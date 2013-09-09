from Acquisition import aq_inner
from fourdigits.portlet.twitter import twitter
from fourdigits.portlet.twitter import \
    FourdigitsPortletTwitterMessageFactory as _
from plone.app.portlets.portlets import base
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from time import time
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
import re


def _cache_key(func, self):
    # context = aq_inner(self.context)
    registry = getUtility(IRegistry)
    reg = registry.get(
        'fourdigits.portlet.twitter.controlpanel.interfaces' +
        '.IFourdigitPortletTwitterSetting.cache_time',
        None)
    if reg:
        cache_time = reg
    else:
        cache_time = 300  # default 300s
    username = self.data.username
    searchterms = self.data.search
    userdisplay = self.data.userdisplay
    searchdisplay = self.data.searchdisplay
    searchlimit = self.data.searchlimit
    filtertext = self.data.filtertext
    languages = self.data.language
    userpictures = self.data.userpictures
    includerts = self.data.includerts
    cache_time_key = time() // (cache_time)
    consumer_key = self.data.consumer_key
    consumer_secret = self.data.consumer_secret
    access_token_key = self.data.access_token_key
    access_token_secret = self.data.access_token_secret
    return (cache_time_key, func.__name__, username, searchterms, userdisplay,
            searchdisplay, searchlimit, filtertext, languages, userpictures,
            includerts, consumer_key, consumer_secret, consumer_secret,
            access_token_key, access_token_secret)

# Match and capture urls
urlsRegexp = re.compile(r"""
    (
    # Protocol
    http://
    # Alphanumeric, dash, slash or dot
    [A-Za-z0-9\-/?=&.\_]*
    # Don't end with a dot
    [A-Za-z0-9\-/]+
    )
    """, re.VERBOSE)

# Match and capture #tags
hashRegexp = re.compile(r"""
    # Hash at start of string or after space, followed by at least one
    # alphanumeric or dash
    (?:^|(?<=\s))\#([A-Za-z0-9\-\_]+)
    """, re.VERBOSE)

# Match and capture @names
atRegexp = re.compile(r"""
    # At symbol at start of string or after space, followed by at least one
    # alphanumeric or dash
    (?:^|(?<=\s))@([A-Za-z0-9\-\_]+)
    """, re.VERBOSE)

# Match and capture email address
emailRegexp = re.compile(r"""
    # Email at start of string or after space
    (?:^|(?<=\s))([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})\b
    """, re.VERBOSE | re.IGNORECASE)


def expand_tweet(str):
    """This method takes a string, parses it for URLs, hashtags and mentions
       and returns a hyperlinked string."""

    str = re.sub(urlsRegexp, '<a href="\g<1>">\g<1></a>', str)
    str = re.sub(hashRegexp,
                 '<a href="http://twitter.com/search?q=%23\g<1>">#\g<1></a>',
                 str)
    str = re.sub(atRegexp,
                 '<a href="http://twitter.com/\g<1>">@\g<1></a>',
                 str)
    str = re.sub(emailRegexp,
                 '<a href="mailto:\g<1>">\g<1></a>',
                 str)
    return str


class IFourdigitsPortletTwitter(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    name = schema.TextLine(
        title=_("twitterportlet_title", default=u"Title"),
        description=_("twitterportlet_title_help",
                      default=u"The title of the portlet."))

    username = schema.TextLine(
        title=_("twitterportlet_username", default=u"Username"),
        description=_("twitterportlet_username_help",
                      default=u"The tweets of this user will be shown."),
        required=False,)

    userinfo = schema.Bool(
        title=_("twitterportlet_userinfo", default=u"Show user info?"),
        description=_("twitterportlet_userinfo_help",
                      default=u"Show info of the Twitter user? (username is mandatory)."),
        required=False,)

    includerts = schema.Bool(
        title=_("twitterportlet_includerts", default=u"Include retweets"),
        description=_("twitterportlet_includerts_help",
                      default=u"Include retweets of the user's account?"),
        required=False,
        default=True,)

    mergeuserandsearch = schema.Bool(
        title=_("twitterportlet_mergeuserandsearch",
                default=u"Merge results from username and search terms?"),
        description=_("twitterportlet_mergeuserandsearch_help",
                      default=u"Make a search for tweets made by the given user with some additional search terms."),
        required=False,
        default=False,)

    search = schema.Text(
        title=_("twitterportlet_search",
                default=u"Search"),
        description=_("twitterportlet_search_help",
                      default=u"""The tweets containing this text will
                      be shown enter one per line, hashtags are allowed."""),
        required=False,)

    filtertext = schema.Text(
        title=_("twitterportlet_filtertext",
                default=u"Filtertext"),
        description=_("twitterportlet_filtertext_help",
                      default=u"""If a message containes (curse) words
                      in the filtertext it wont be shown, one per line.
                      this currently works on the serverside implementation."""),
        required=False,)

    userdisplay = schema.Int(
        title=_("twitterportlet_userdisplay",
                default=u'Number of items to display based on the username'),
        description=_("twitterportlet_userdisplay_help",
                      default=u'How many items to list based on the username.'),
        required=False,
        default=5,
    )
    searchdisplay = schema.Int(
        title=_("twitterportlet_searchdisplay",
                default=u'Number of items to display based on the searchtext'),
        description=_("twitterportlet_searchdisplay_help",
                      default=u'How many items to list based on the searchtext.'),
        required=False,
        default=5,
    )

    searchlimit = schema.Int(
        title=_("twitterportlet_searchlimit",
                default=u'Number of items to search for, defaults to 40'),
        description=_("twitterportlet_searchlimit_help",
                      default=u'Number of items to search for, defaults to 40.'),
        required=True,
        default=40,
    )

    language = schema.Text(
        title=_("twitterportlet_language",
                default=u"Languagefilter"),
        description=_("twitterportlet_language_help",
                      default=u"""Language ISO code for the tweets (e.g.: en, nl, fr),
                      if you like to filter on language one per line."""),
        required=False,
    )

    userpictures = schema.Bool(
        title=_("twitterportlet_userpictures",
                default=u"Show user pictures?"),
        description=_("twitterportlet_userpictures_help",
                      default=u"Should the portlet show the twitter user pictures?"),
        default=True,
    )

    footer_text = schema.Text(
        title=_("twitterportlet_footer_text",
                default=u'Line rendered in the portlet footer'),
        description=_("twitterportlet_footer_text_help",
                      default=u'You can include a link.'),
        required=False,
    )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IFourdigitsPortletTwitter)
    includerts = True
    userinfo = True
    mergeuserandsearch = False
    footer_text = ""
    consumer_key = ''
    consumer_secret = ''
    access_token_key = ''
    access_token_secret = ''

    def __init__(self, name=u"", username=u"", search=u"", filtertext="",
                 userdisplay=5, searchdisplay=5, searchlimit=40,
                 language="", userpictures=False, includerts=True,
                 mergeuserandsearch=False, userinfo=False, consumer_key='',
                 consumer_secret='', access_token_key='',
                 access_token_secret='', footer_text=""):
        self.name = name
        self.username = username
        self.search = search
        self.filtertext = filtertext
        self.userdisplay = userdisplay
        self.searchdisplay = searchdisplay
        self.searchlimit = searchlimit
        self.language = language
        self.userpictures = userpictures
        self.includerts = includerts
        self.mergeuserandsearch = mergeuserandsearch
        self.userinfo = userinfo
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret
        self.footer_text = footer_text

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Portlet Twitter"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    _template = ViewPageTemplateFile('fourdigitsportlettwitter.pt')

    def render(self):
        return xhtml_compress(self._template())

    @property
    def title(self):
        return self.data.name or _(u"Tweets")

    @property
    def normalized_title(self):
        normalizer = getUtility(IIDNormalizer)
        return normalizer.normalize(self.title)

    @property
    def available(self):
        return True

    def language(self):
        """
        @return: Two-letter string, the active language code
        """
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        current_language = portal_state.language()
        return current_language.split('-')[0]

    def expand(self, str):
        return expand_tweet(str)

    def showuserinfo(self):
        """Should we show userinfo"""
        if self.data.userinfo:
            return True
        return False

    def getuserinfo(self):
        registry = getUtility(IRegistry)
        reg = registry.get(
            'fourdigits.portlet.twitter.controlpanel.interfaces' +
            '.IFourdigitPortletTwitterSetting.use_data_cache',
            None)
        if reg:
            return self.cached_userinfo()
        else:
            return self._getuserinfo()

    def _getuserinfo(self):
        """Get twitter user info"""
        userinfo = self.twapi.GetUser(screen_name=self.data.username)
        return userinfo

    @ram.cache(_cache_key)
    def cached_userinfo(self):
        return self._getuserinfo()

    def twittermessages(self):
        """Twitter messages"""
        return self._data()

    def _data(self):
        registry = getUtility(IRegistry)
        reg = registry.get(
            'fourdigits.portlet.twitter.controlpanel.interfaces' +
            '.IFourdigitPortletTwitterSetting.use_data_cache',
            None)
        if reg:
            return self.cached_tweets()
        else:
            return self.gettweets()

    def gettweetsofuser(self, username, userpictures, includerts):
        """Return the tweets of a certain user"""
        try:
            tweets = self.twapi.GetUserTimeline(screen_name=username,
                                                include_rts=includerts)
        except:
            tweets = []
        return tweets

    def gettweetsbysearch(self, query_dict):
        """Return tweets based on a search query"""
        try:
            tweets = self.twapi.GetSearch(**query_dict)
        except:
            tweets = []
        return tweets

    def _init_twitter_api(self):
        registry = getUtility(IRegistry)
        consumer_key = registry.get(
            'fourdigits.portlet.twitter.controlpanel.interfaces' +
            '.IFourdigitPortletTwitterSetting.consumer_key', None)
        consumer_secret = registry.get(
            'fourdigits.portlet.twitter.controlpanel.interfaces' +
            '.IFourdigitPortletTwitterSetting.consumer_secret', None)
        access_token_key = registry.get(
            'fourdigits.portlet.twitter.controlpanel.interfaces' +
            '.IFourdigitPortletTwitterSetting.access_token_key', None)
        access_token_secret = registry.get(
            'fourdigits.portlet.twitter.controlpanel.interfaces' +
            '.IFourdigitPortletTwitterSetting.access_token_secret', None)

        self.twapi = twitter.Api(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_key=access_token_key,
            access_token_secret=access_token_secret,
            debugHTTP=False
        )

    def gettweets(self):
        """Get the tweets and filter them"""
        username = self.data.username
        searchterms = self.data.search
        userdisplay = self.data.userdisplay
        searchdisplay = self.data.searchdisplay
        searchlimit = self.data.searchlimit
        filtertext = self.data.filtertext
        languages = self.data.language
        userpictures = self.data.userpictures
        includerts = self.data.includerts

        self._init_twitter_api()
        results = []
        tweets = []

        # get tweets of username
        if username:
            tweets = self.gettweetsofuser(username,
                                          userpictures,
                                          includerts)
        tweets = tweets[:userdisplay]

        searchresults = []
        # get tweets based on search
        if searchterms:
            searchterms = searchterms.encode('utf-8')
            searchterms_list = searchterms.split('\n')
            #remove empty lines
            searchterms_list = [term for term in searchterms_list if term]
            searchterms = ' OR '.join(searchterms_list)
            query_dict = {'term': searchterms,
                          'count': searchlimit,
                          'lang': ""}
            if self.data.mergeuserandsearch:
                query_dict['from_user'] = self.data.username
            if languages:
                languages = languages.split('\n')
                for lang in languages:
                    lang = str(lang.encode('utf-8'))
                    query_dict['lang'] = lang
                    searchresults += self.gettweetsbysearch(query_dict)
            else:
                searchresults += self.gettweetsbysearch(query_dict)
            # Only add tweets which are not already in the user results
            filtered_results = [tweet for tweet in searchresults
                                if not tweet in tweets]
            tweets += filtered_results[:searchdisplay]

        if filtertext:
            filtertext = filtertext.lower()
            filterlist = filtertext.split('\n')

        # add picture and filter out tweets based on the filterlist
        for tweet in tweets:
            tweet.username = tweet.user.GetScreenName()
            picture = tweet.user.GetProfileImageUrl()
            tweet.author_url = 'http://twitter.com/%s' % tweet.username
            if userpictures:
                tweet.picture = picture

            # remove double usernames in message
            usernameLength = len(tweet.username) + 1
            if tweet.text[0:usernameLength] == (tweet.username + ":"):
                tweet.text = tweet.text[usernameLength:len(tweet.text)]

            if filtertext:
                text = tweet.text.lower()
                if not [1 for x in filterlist if x in text]:
                    results.append(tweet)
            else:
                results.append(tweet)
        tweets = results

        # sort the tweets
        tweets.sort(key=lambda tweet: tweet.GetCreatedAtInSeconds())
        tweets.reverse()

        return tweets

    @ram.cache(_cache_key)
    def cached_tweets(self):
        return self.gettweets()


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IFourdigitsPortletTwitter)
    label = _(u"Twitter portlet")
    description = _(u"""This portlet displays tweets. Please keep note
                    that some settings will apply after 5 minutes.""")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IFourdigitsPortletTwitter)
    label = _(u"Twitter portlet")
    description = _(u"""This portlet displays tweets. Please keep note
                    that some settings will apply after 5 minutes.""")
