'''
Created on Sep 27, 2013

@author: "Colin Manning"
'''
import requests
import json
import os

dropbox_root = '/home/colin/Dropbox/printflow/SAB'
url = 'http://dis.printflow2.com/search/sab/category?path=$Categories'

def ensureDirectoryExists(path):
    if not os.path.exists(path):
        os.makedirs(path, mode=0o755)

def process_subcategory(parent, cat):
    path = os.path.join(parent, cat['name'])
    ensureDirectoryExists(path)
    if 'subcategories' in cat:  
        subcats = cat['subcategories']  
        for i in range(len(subcats)):
            process_subcategory(path, subcats[i])
        
    
response = requests.post(url)
if response.status_code == 200:
    # now link to category
    r = response.json()
    subcategories = r['subcategories']
    for i in range(len(subcategories)):
        process_subcategory(dropbox_root, subcategories[i])
