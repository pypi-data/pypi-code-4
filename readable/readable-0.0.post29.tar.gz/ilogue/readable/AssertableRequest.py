from ilogue.readable.AssertableDocument import AssertableDocument
from ilogue.readable.AssertableFileResponse import AssertableFileResponse
import requests


class AssertableRequest(object):

    def __init__(self, url, method="GET"):
        self.url = url
        self.method = method.upper()

    def returnsDocument(self):
        response = self.send()
        return AssertableDocument(response.text)

    def returnsFile(self):
        response = self.send()
        return AssertableFileResponse(response)

    def returnsCode(self,code):
        response = self.send()
        if not response.status_code == code:
            msg = 'Expected HTTP status code {0}, got {1}.'
            raise AssertionError(msg.format(code,response.status_code))

    def send(self):
        try:
            if self.method == "GET":
                response = requests.get(self.url, timeout=3)
            elif self.method == "POST":
                response = requests.post(self.url, timeout=3)
            else:
                raise ValueError("Unknown method: "+str(self.method))
            response.raise_for_status()
        except requests.ConnectionError as e: 
            raise AssertionError(e)
        except requests.HTTPError as e: 
            raise AssertionError(e)
        except requests.TooManyRedirects as e: 
            raise AssertionError(e)
        return response

#    def get(self, url):
#        page = self.tryUrlOpen(url)
#        #return AssertablePage(page[:8192])

#    # try to get the server internal traceback from the HTTP response content
#    def tryGetTraceback(self, httpError):
#        trace = '  '
#        try:
#            content = httpError.read()
#            soup = BeautifulSoup(content)
#            textVersionDivs = soup.findAll("div",id="short_text_version")
#            if textVersionDivs:
#                area = textVersionDivs[0].textarea
#                trace += area.string
#            else:
#                trace += '[No Pyramid traceback found]'
#        except Exception as err:
#            trace += str(err)
#        return trace

if __name__ == '__main__':
    print(__doc__)

