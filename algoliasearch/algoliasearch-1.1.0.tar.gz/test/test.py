from algoliasearch import algoliasearch
# -*- coding: utf-8 -*-
import pprint
import json
import time
import datetime

client = algoliasearch.Client("algoliabot", 'c42b3421ee31b6083e5ce1f5b9111426', ["c1-eu-4.algolia.io", "c1-eu-5.algolia.io", "c1-eu-6.algolia.io"])
#client = algoliasearch.Client("MySuperApp", '20ffce3fdbf036db955d67645bb2c993', ["localhost.algolia.com:8080"])
client.copyIndex("MySuperIndex", "MySuperIndex10")
client.copyIndex("MySuperIndex3", "MySuperIndex30")
#try:
#    client.deleteIndex("eu-probe")
#except:
#    pass
#index = client.initIndex("eu-probe")
#index.addObject({"firstname": "Jimmie", "lastname": "Barninger"})
#time.sleep(1)
#start = datetime.datetime.now()
#res = index.search("jim")
#end = datetime.datetime.now()
#delta = end - start
#print 'Time : ' + str(delta.total_seconds())

#start = time.time()
#client.listIndexes()
#end = time.time()
#print (end - start)
#
#start = time.time()
#client.listIndexes()
#end = time.time()
#print (end - start)
#print client.listIndexes()
#index = client.initIndex("toto")

#res = index.saveObjects([{"name": "San Francisco", 
#                         "population": 805235,
#                         "objectID": "SFO"},
#                        {"name":"Los Angeles",
#                         "population":3792621,
#                         "objectID":"LA"}])
#index.waitTask(res["taskID"])

#client.addUserKey(["search"], 300)
#print client.getUserKeyACL("55bb15dacd5f77b772b9a68704b7aa6d")
#print client.deleteUserKey("55bb15dacd5f77b772b9a68704b7aa6d")
#print client.listUserKeys()
# List API Keys that can access only to this index
#res = index.addUserKey(["search"], 300)
#print index.listUserKeys()

#print index.search(u'ééé')
#print index.getUserKeyACL("74dec0fc7c19ed57a8239e4644b8989c")
#print index.deleteUserKey("74dec0fc7c19ed57a8239e4644b8989c")
#settings = index.getSettings();
#settings["customRanking"] = ["desc(population)", "asc(name)"]
#pprint.pprint(index.setSettings(settings))
