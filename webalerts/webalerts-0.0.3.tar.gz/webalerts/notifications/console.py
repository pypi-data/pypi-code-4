from __future__ import print_function


class ConsoleNotification(object):
    """
    Prints the titles and URLs of the matched posts to the standard out. It is
    intended to be used for debugging.

    There are no configuration values for this notification.

    """

    def __init__(self, config):
        pass

    def notify(self, posts):
        if not posts:
            print('No posts')
        for post in posts:
            print(post.title, post.url)
