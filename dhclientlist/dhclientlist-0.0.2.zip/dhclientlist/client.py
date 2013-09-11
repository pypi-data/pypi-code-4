
import requests
from requests.auth import HTTPBasicAuth

response = requests.get('https://localhost:10023/?format=json', verify=False)#, auth=HTTPBasicAuth('admin', '123'))
print response.status_code
print response.content
