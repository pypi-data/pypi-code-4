# coding=utf8

"""this is the main processor when lilac building"""


import signals
from .config import config
from .parser import parser
from .renderer import renderer
from .exceptions import *
from .logger import logger, logging
from .utils import chunks, update_nested_dict, mkdir_p, join
from .models import Post, Tag, Page
from .models import blog, author, about, tags, archives, feed, page_404, charset

import sys
import toml
from os.path import exists
from datetime import datetime
from pyatom import AtomFeed


class Generator(object):

    def __init__(self):
        """init attributes to store runtime data"""
        # initialize them the default value.
        self.reset()
        # register signals
        self.register_signals()

    def reset(self):
        """reset all posts, tags, pages .etc."""
        self.posts = []
        self.tags = []
        self.pages = []
        self.about = about
        self.blog = blog
        self.author = author
        self._tags = tags
        self.archives = archives
        self.feed = feed
        self.page_404 = page_404
        self.config = config.default
        self.root_path = ''
        self.theme = {}

    def register_signals(self):
        """Register all signals in this process"""
        signals.initialized.connect(self.parse_posts)
        signals.initialized.connect(self.render_about_page)
        signals.initialized.connect(self.render_page_404)
        signals.posts_parsed.connect(self.extract_tags)
        signals.posts_parsed.connect(self.compose_pages)
        signals.posts_parsed.connect(self.render_posts)
        signals.posts_parsed.connect(self.render_archives)
        signals.posts_parsed.connect(self.generate_feed)
        signals.tags_extracted.connect(self.render_tags)
        signals.page_composed.connect(self.render_pages)

    def step(step_method):
        """decorator to wrap each step method"""
        def wrapper(self, *args, **kwargs):
            logger.info(step_method.__doc__)
            return step_method(self, *args, **kwargs)
        return wrapper

    @step
    def initialize(self, localhost):
        """Initialize config, blog, author, feed and jinja2 environment"""
        # read config to update the default
        try:
            conf = config.read()
        except ConfigSyntaxError as e:
            logger.error(e.__doc__)
            sys.exit(1)

        update_nested_dict(self.config, conf)
        # update blog and author according to configuration
        self.blog.__dict__.update(self.config['blog'])
        self.author.__dict__.update(self.config['author'])
        # reset root_path if not in localhost
        if not localhost:
            self.root_path = self.config["root_path"]
        # initialize feed
        self.feed.feed = AtomFeed(
            title=self.blog.name,
            subtitle=self.blog.description,
            feed_url=self.blog.url+"/feed.atom",
            url=self.blog.url,
            author=self.author.name
        )
        #
        # -------- initialize jinja2 --
        #
        # detect if there is a theme.toml
        theme_toml = join(self.blog.theme, "theme.toml")

        if exists(theme_toml):
            self.theme = toml.loads(open(theme_toml).read().decode(charset))
        # update theme_conf with config's theme section
        # user's configuation can reset theme's configuation
        config_theme_section = self.config.get("theme", {})
        update_nested_dict(self.theme, config_theme_section)

        # get templates directory
        templates = join(self.blog.theme, "templates")
        # set a render
        jinja_global_data = dict(
            root_path=self.root_path,
            blog=self.blog,
            author=self.author,
            config=self.config,
            theme=self.theme
        )
        renderer.initialize(templates, jinja_global_data)
        logger.success("Generator initialized, root_path = \"%s\"" % self.root_path)
        # send signal that generator was already initialized
        signals.initialized.send(self)

    # make alias to initialize
    generate = initialize

    def re_generate(self, localhost):
        """Reset generator's data and build"""
        self.reset()
        self.generate(localhost)

    @step
    def parse_posts(self, sender):
        """Parse posts and sort them by create time"""
        # glob all source files
        try:
            files = Post.glob_src_files()
        except SourceDirectoryNotFound as e:
            logger.error(e.__doc__)
            sys.exit(1)

        # parse each post's content and append post instance to self.posts
        for filepath, name in files.iteritems():
            try:
                post = parser.parse_from(filepath)
            except ParseException, e:
                logger.warn(e.__doc__ + ": filepath '%s'" % filepath)
                pass  # skip the wrong parsed post
            else:
                post.name = name  # set it a name attribute
                self.posts.append(post)
        # sort posts by its create time
        self.posts.sort(
            key=lambda post: post.datetime.timetuple(),  # from now to past
            reverse=True
        )
        logger.success("Posts parsed")
        signals.posts_parsed.send(self)

    @step
    def extract_tags(self, sender):
        """Extract tags from posts, and sort by their posts' amount"""
        # traversal all posts and get the minial tag to posts dict
        tags = {}

        for post in self.posts:
            for tag in post.tags:
                tags.setdefault(tag, []).append(post)

        # initialize tags
        for tag, posts in tags.iteritems():
            self.tags.append(Tag(tag, posts))

        # sort by tag's size
        self.tags.sort(key=lambda x: len(x.posts), reverse=True)
        logger.success("Tag extracted")
        signals.tags_extracted.send(self)

    @step
    def compose_pages(self, sender):
        """Compose pages from posts"""
        # Actually I don't want to put this as a configuation item
        # but some themes need this, so lilac gets it from theme's conf,
        # by default: 7
        posts_count_per_page = self.theme.get("posts_count_per_page", 7)

        groups = chunks(self.posts, posts_count_per_page)  # 7 posts per page

        for index, group in enumerate(groups):
            self.pages.append(Page(number=index+1, posts=list(group)))

        if self.pages:  # must not empty
            self.pages[0].first = True
            self.pages[-1].last = True
        logger.success("Pages composed")
        signals.page_composed.send(self)

    def render_to(self, path, template, **data):
        """shortcut to render data with template and then write to path.
        Just add exception catch to renderer.render_to"""
        try:
            renderer.render_to(path, template, **data)
        except JinjaTemplateNotFound as e:
            logger.error(e.__doc__ + ": Template '%s'" % template)
            sys.exit(1)  # template not found,  must exit the script

    @step
    def render_posts(self, sender):
        """Render all posts to 'post/' with template 'post.html'"""
        mkdir_p(Post.out_dir)

        for post in self.posts:
            self.render_to(post.out, Post.template, post=post)

        logger.success("Posts rendered")

    @step
    def render_tags(self, sender):
        """Render all tags to 'tag/' with template 'tag.html'"""
        mkdir_p(Tag.out_dir)

        for tag in self.tags:
            self.render_to(tag.out, Tag.template, tag=tag)

        self.render_to(self._tags.out, self._tags.template, tags=self.tags)
        logger.success("Tags rendered")

    @step
    def render_pages(self, sender):
        """Render all pages to 'page/' with template 'page.html'"""
        mkdir_p(Page.out_dir)

        for page in self.pages:
            self.render_to(page.out, Page.template, page=page)
        logger.success("Pages rendered")

    @step
    def render_archives(self, sender):
        """Render archives page to 'archives.html' with template 'archives.html'"""
        self.render_to(self.archives.out, self.archives.template, posts=self.posts)
        logger.success("Archives rendered")

    @step
    def render_about_page(self, sender):
        """Render about me page to 'about.html' with template 'about.html'"""
        about = self.about
        about.markdown = parser.markdown.render(about.content)
        self.render_to(about.out, about.template, about=about)
        logger.success("About page rendered")

    @step
    def generate_feed(self, sender):
        """Generate feed for first 10 posts to 'feed.atom'"""
        for post in self.posts[:self.feed.size]:
            try:
                self.feed.feed.add(
                    title=post.title,
                    content=post.html,
                    content_type="html",
                    author=self.author.name,
                    url=self.blog.url + "/" + post.out,
                    updated=post.datetime
                )
            except Exception as e:
                logger.warning(str(e))
                pass  # skip

        self.feed.write()
        logger.success("Feed generated")

    @step
    def render_page_404(self, sender):
        """Render 404 page to '404.html' with template '404.html' """
        self.render_to(self.page_404.out, self.page_404.template)
        logger.success("404 rendered")

generator = Generator()
