# coding=utf8

"""models in lilac: Blog, Author, Post, Tag, Page"""


from .exceptions import SourceDirectoryNotFound
from . import src_ext, out_ext, src_dir, out_dir, charset

from hashlib import md5
from os import listdir as ls
from os.path import exists
from .utils import join


class Blog(object):
    """
    The blog itself.
    attributes
      name        unicode     blog's name
      description unicode     blog's description
      url         str         blog's site url
      theme   str             which theme to use
    """

    def __init__(self, name=None, description=None, url=None, theme=None):
        self.name = name
        self.description = description
        self.url = url
        self.theme = theme


blog = Blog()


class Author(object):
    """
    The blog's author, only one.
    attributs
      name          unicode     author's name
      email         unicode     author's email
      gravatar_id   str         gravatar_id generated from email
    the gravatar_id is a property decorated method.
    """

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    @property
    def gravatar_id(self):
        """it's md5(author.email), author's gravatar_id"""
        return md5(self.email).hexdigest()


author = Author()

class Post(object):
    """
    The blog's post(s).
    attributes
      name      str      post's filename without extension
      title     unicode  post's title
      datetime  datetime post's create time, e.g. "2012-10-10 13:20"
      tags      list     post's tags
      markdown  unicode  post's markdown source(its body)
      html      unicode  post's html(parrsed from markdown)
    the `html` is a property decorated method
    """

    src_dir = join(src_dir, "post")  # src directroy of posts
    out_dir = join(out_dir, "post")  # html directroy of posts
    template = "post.html"  # all posts are rendered with this template

    def __init__(
        self,
        name=None, tags=None, title=None, datetime=None, markdown=None,
        **other_attrs
    ):
        self.name = name
        self.title = title
        self.datetime = datetime
        self.markdown = markdown

        if tags is None:
            self.tags = []
        else:
            self.tags = tags

        self.__dict__.update(other_attrs)

    @property
    def html(self):
        """Return the post's content's rendered markdown"""
        # the parser should be import in method, else will cause annoying loop
        # import issue
        from .parser import parser
        return parser.markdown.render(self.markdown)

    def __getattr__(self, key):
        if key == "summary":  # if no summary defined in post's header return the first 200 char
            return self.slice(0, 200)
        else:
            raise AttributeError

    def slice(self, start=0, end=200):
        """render post's body's some slice to html, and return it"""
        from .parser import parser
        return parser.markdown.render(self.markdown[start:end])


    @property
    def src(self):
        """Return the post's source filepath"""
        return join(Post.src_dir, self.name + src_ext)

    @property
    def out(self):
        """Return the post's output(html) filepath"""
        return join(Post.out_dir, self.name + out_ext)

    @classmethod
    def glob_src_files(cls):
        """Glob source files return filepath to name dict"""

        if not exists(Post.src_dir):
            raise SourceDirectoryNotFound

        dct = {}

        for fn in ls(Post.src_dir):
            if fn.endswith(src_ext):
                name = fn[:-len(src_ext)]
                path = join(Post.src_dir, fn)
                dct[path] = name

        return dct


class Tag(object):
    """
    Each posts may have tags, each tag has some posts.
    attributes
      name      unicode     tag's name
      posts     list        posts in this tag
    """

    out_dir = join(out_dir, "tag")
    template = "tag.html"

    def __init__(self, name=None, posts=None):
        self.name = name

        if posts is None:
            self.posts = []
        else:
            self.posts = posts

    @property
    def out(self):
        """return this tag's output filepath"""
        return join(Tag.out_dir, self.name + out_ext)


class Page(object):
    """
    The pages, 1st, 2nd, 3rd page..
    attributes
      number    int   the order of this page
      posts     list  the posts in this page
      first     bool  is this page the first page?
      last      bool  is this page the last page
    """

    template = "page.html"
    out_dir = join(out_dir, "page")

    def __init__(self, number=1, posts=None, first=False, last=False):
        self.number = number
        self.first = first
        self.last = last

        if posts is None:
            self.posts = []
        else:
            self.posts = posts

    @property
    def out(self):
        if self.first:
            return join(out_dir, "index" + out_ext)
        else:
            return join(Page.out_dir, str(self.number) + out_ext)


class About(object):
    """
    The blog's about page, only one.
    attributes
      markdown  its content
      html      its markdown's html
    about has no header, only body in markdown.
    the `html` is a property decorated method.
    """

    def __init__(self, markdown=None):
        self.markdown = markdown
        self.src = join(src_dir, "about" + src_ext)
        self.out = join(out_dir, "about" + out_ext)
        self.template = "about.html"

    @property
    def html(self):
        """Render its markdown to html"""
        from .parser import parser
        return parser.markdown.render(self.markdown)

    @property
    def content(self):
        """open source file and return the content"""
        if exists(self.src):
            return open(self.src).read().decode(charset)
        else:
            return u''


about = About()

class Tags(object):
    """
    the 'tags.html' of this blog, it displays all tags
    in single page.
    """

    def __init__(self):
        self.template = "tags.html"
        self.out = join(out_dir, "tags" + out_ext)


tags = Tags()

class Archives(object):
    """the 'archives.html' of this blog, it displays all posts
    in single page."""

    def __init__(self):
        self.template = "archives.html"
        self.out = join(out_dir, "archives" + out_ext)


archives = Archives()

class Feed(object):
    """the feed 'feed.atom'"""

    size = 10

    def __init__(self, feed=None):
        self.feed = feed  # pyatom feed object
        self.out = join(out_dir, "feed.atom")

    def write(self):
        """write feed to file"""
        return open(self.out, "w").write(self.feed.to_string().encode(charset))


feed = Feed()

class Page404(object):
    """page 404.html"""

    def __init__(self):
        self.out = join(out_dir, "404" + out_ext)
        self.template = "404.html"


page_404 = Page404()
