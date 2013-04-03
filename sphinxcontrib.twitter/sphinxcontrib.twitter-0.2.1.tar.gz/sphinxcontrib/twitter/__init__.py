#-*- coding:utf-8 -*-
u'''
embedding twitter's tweet in sphinx

usage:

First of all, add `sphinx_tweet_embed` to sphinx extension list in conf.py

.. code-block:: python

   extensions = ['sphinxcontrib.twitter']


then use `tweet` directive and `tw` role.

.. code-block:: rst

   .. tweet:: https://twitter.com/pypi/status/315214320826978305

   :tw:`@shomah4a`


finally, build your sphinx project.


.. code-block:: sh

   $ make html
'''

__version__ = '0.2.1'
__author__ = '@shomah4a'
__license__ = 'LGPLv3'



def setup(app):

    from . import tweet, user

    app.add_javascript('http://platform.twitter.com/widgets.js')

    app.add_node(tweet.tweet,
                 html=(tweet.visit, tweet.depart))
    app.add_directive('tweet', tweet.TweetDirective)

    app.add_node(user.twnode,
                 html=(user.visit, user.depart))
    app.add_role('tw', user.tw_role)

