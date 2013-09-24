from bs4 import BeautifulSoup
from ilogue.readable import assertRequest


class FormInteraction(object):


    def __init__(self, contents, requester=assertRequest):
        self.request = requester
        self.contents = contents

    def submit(self):
        form = BeautifulSoup(self.contents).form
        self.url = form['action']
        if form.has_key('method'):
            method = form['method']
        else:
            method = "POST"
        return self.request(self.url, method=method)
