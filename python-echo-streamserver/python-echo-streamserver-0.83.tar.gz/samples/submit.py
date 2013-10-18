from echo import items
from pprint import pprint

test_data="""<?xml version="1.0" encoding="UTF-8"?>
<feed
 xml:lang="en-US" xmlns="http://www.w3.org/2005/Atom"
 xmlns:activity="http://activitystrea.ms/spec/1.0/"
 xmlns:thr="http://purl.org/syndication/thread/1.0"
 xmlns:media="http://purl.org/syndication/atommedia"
 xmlns:service="http://activitystrea.ms/service-provider">


  <id>http://example.com/2</id>
  <generator uri="http://example.com/">JS-Kit.com Syndication</generator>
  <title>Comments AS feed</title>
  <link rel="alternate" href="/http://example.com/2" type="text/html"/>
  <link rel="self" href="/http://example.com/atom/2" type="application/atom+xml"/>
  <updated>2009-11-27T17:03:21+00:00</updated>
  <icon>http://example.com/favicon.ico</icon>
  <logo>http://example.com/images/site/logo8.png</logo>
  <entry>
    <id>http://example.com/entryid-1252922924-934</id>
    <published>2009-11-27T17:01:55+00:00</published>
    <updated>2009-11-27T17:01:55+00:00</updated>
    <title>Some string</title>
    <link rel="alternate" type="text/html" href="/http://example.com/page.html#jsid-1252922924-934"/>
    <author>
      <name>Test User</name>
    </author>
    <activity:verb>http://activitystrea.ms/schema/1.0/post</activity:verb>
    <activity:actor>
      <activity:object-type>http://activitystrea.ms/schema/1.0/person</activity:object-type>
      <id>http://example.com/user/k9SmUHp4RARWtdzsb5KscA</id>
      <title>Test User</title>
      <uri>http://example.com/</uri>
      <email>test@example.com</email>
      <link rel="alternate" type="text/html" href="/http://example.com/TestUser"/>
      <link rel="avatar" type="image/png" href="/http://example.com/blob/gxpA99f0jKlohF_DgthroT.png" media:width="100" media:height="100"/>
    </activity:actor>
    <activity:object>
      <activity:object-type>http://activitystrea.ms/schema/1.0/comment</activity:object-type>
      <id>http://example.com/jsid-1252922924-934</id>
      <content type="html">&lt;b&gt;Test comment&lt;/b&gt;</content>
      <published>2009-11-27T17:01:55+00:00</published>
      <link rel="alternate" type="text/html" href="/http://example.com/page.html#jsid-1252922924-934"/>
      <thr:in-reply-to ref="http://example.com/1" type="text/html" href="/http://example.com/1"/>
    </activity:object>
    <activity:target>
      <activity:object-type>http://activitystrea.ms/schema/1.0/article</activity:object-type>
      <id>http://example.com/page1</id>
    </activity:target>
  </entry>
</feed>"""

result = items.submit(content=test_data)
pprint(result)

