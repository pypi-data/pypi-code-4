#
# chinatimes.py
#
# Copyright 2012 - 2013 Louie Lu <grapherd at gmail.com>
#
#

"""
newstitle chinatimes module
"""

import codecs
import httplib2
import lxml.html

base_url = "http://news.chinatimes.com"
news_list_url = "http://news.chinatimes.com/rtnlist/0/0/100/1.html"

h = httplib2.Http(".cache")

def get_realtime_title():
    """Get ALL Category and Source Realtime news from chinatimes
    realtime url may change or invaild when it is not *realtime*
            
    return: dict{category, source, time, title, url}
    """
    
    response, content = h.request(news_list_url)

    html = lxml.html.fromstring(content.decode('big5', 'ignore'))
    html.make_links_absolute(base_url)

    # Get news-list section
    div = html.findall("*div")[1]

    # Get all title-info to list
    tr = list(div.iterdescendants("tr"))[1:]

    result_list = []
    for title_info in tr:
        news_url = list(title_info.iterlinks())[0][2]
        info_list = map(lambda x: x.text_content(), list(title_info))

        info_dict = {"title": info_list[0].strip("\r\n "), "time": info_list[1],
                     "category": info_list[2], "source": info_list[3],
                     "url": news_url}
    
        result_list.append(info_dict)
        
    return result_list

def save_realtime_title(filename="chinatime_realtime_title.csv",
                        append=False, sep=","):
    """Save chinatimes realtime title to CSV file.

    *kwargs*:
        filename -- csv file name
        append -- append to old file
        sep -- the separated value for csv file
    """
    
    title_info = get_realtime_title()
    
    if append:
        pass
    else:
        fo = codecs.open(filename, "w", "utf-8")
        fo.write('"title", "time", "url"\n')
        for info in title_info:
            fo.write('"%s"%s "%s"%s "%s"\n' %
                     (info['title'], sep, info['time'], sep, info['url']))
        
        fo.close()

if __name__ == '__main__':
    pass