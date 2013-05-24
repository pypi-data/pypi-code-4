#Flipkart Books API
#Author Vengadanathan

import urllib2
import urllib
from bs4 import BeautifulSoup
#class for storing the each item of book search result
class Item:
    pass
class Flipkart:
    def __init__(self):
        pass
    #method that performs search for books with a given query on flipkart
    #arguments are query = book name or part of book name
    #page is the page number to retrieve , increment page number until you receive empty results which would be last page number
    #default page value is 1
    def search(self,query,page=1):
        items = []
        start = 1 + ( (page-1) * 24)
        #flipkart URL used for querying the book
        url = urllib2.urlopen("http://m.flipkart.com/m/m-search-all/searchCategory?q="+urllib.quote_plus(query)+"&store=buk&count=24&otracker=search&start="+str(start)).read()
        soup = BeautifulSoup(url)


        products = soup.find_all("li",{"class":"category-search-result"})

        p = soup.find_all("span",{"class":"note"})[0].string.strip()
        total = [int(s) for s in p.split('(')[1].split() if s.isdigit()][0]
        print total
        for product in products:
            image = product.find_all("img",{"class":"product-image"})[0]['data-src']
            product  = product.find_all("div",{"class":"product-details"})[0]
            title = product.find_all("span",{"class":"product-title"})[0].string.strip()
            product_subtitle = product.find_all("span",{"class":"product-subtitle"})[0].string.strip()
            product_mrp = None
            product_fsp = None
            try:
                product_fsp = product.find_all("span",{"class":"product-price"})[0].find_all("span",{"class":"price-fsp"})[0].string.strip()
            except:
                pass
            try:
                product_mrp = product.find_all("span",{"class":"product-price"})[0].find_all("del",{"class":"price-mrp"})[0].string.strip()
            except:
                pass
            item = Item()
            item.image = image
            item.title = title
            item.product_subtitle = product_subtitle
            item.product_fsp = product_fsp
            item.product_mrp = product_mrp
            items.append(item)
        return items
#example program
#from Flipkart import Flipkart
#from Flipkart import Item
# f = Flipkart()
# items = f.search("data structure")
# for item in items:
    # print item.image
    # print item.title
    # print item.product_subtitle
    # print item.product_fsp
    # print item.product_mrp
