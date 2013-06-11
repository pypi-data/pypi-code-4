
list_rss = ((u'Times Online - Top Stories', u'http://feeds.timesonline.co.uk/c/32313/f/440134/index.rss', u'en'),
            (u'Reuters - Top News', u'http://feeds.reuters.com/reuters/topNews', u'en'),
            (u'Washington Post - World', u'http://feeds.washingtonpost.com/rss/world', u'en'),
            (u'The Guardian - World', u'http://feeds.guardian.co.uk/theguardian/world/rss', u'en'),
            (u'Financial Times - World', u'http://www.ft.com/rss/world', u'en'),
            (u'Telegraph - International News', u'http://www.telegraph.co.uk/news/worldnews/rss', u'en'),
            (u'Daily Mail - World News', u'http://www.dailymail.co.uk/news/index.rss', u'en'),
            (u'The Sun - News', u'http://www.thesun.co.uk/sol/homepage/feeds/rss/article247682.ece', u'en'),
            (u'BBC - News Front Page', u'http://feeds.bbci.co.uk/news/rss.xml?edition=uk', u'en'),
            )


for (name, url, lang) in list_rss:
    session.create_entity('CWSource', name=name, type=u'datafeed',
                          parser=u'rss-parser', lang=lang, url=url,
                          config=u'synchronization-interval=120min')
