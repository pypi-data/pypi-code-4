from youtrack import YouTrackClient
from datetime import datetime

client = YouTrackClient('http://todo.bogdal.pl', api_key="ZGEwYTQ1MWZjODQ0NGVjODdlYWZhMjNmNjg0M2U1ZjE4ODMwYzdkOGNmNTllMjk0Y2FiNTg5YzBmMmNiNjYwMTphYm9nZGFs")



#fields = client.get_project_fields('test')
#for field in fields:
#    print client.get_custom_field_details(field)

issues = client.get_project_issues('agonex')
for issue in issues:
    print '*'*20
    print issue['id']
    print issue.find("field", {'name': 'State'}).text
    print issue.find("field", {'name': 'Priority'}).text
    print issue.find("field", {'name': 'summary'}).text
    timestamp = issue.find("field", {'name': 'created'}).text
    print datetime.fromtimestamp(float(timestamp) / 1e3)
    #print issue.find("field", {'name': 'description'}).text
