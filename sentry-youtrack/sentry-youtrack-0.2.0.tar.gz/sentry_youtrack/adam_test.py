from youtrack import YouTrackClient
from datetime import datetime

client = YouTrackClient('http://todo.bogdal.pl', api_key="ZGEwYTQ1MWZjODQ0NGVjODdlYWZhMjNmNjg0M2U1ZjE4ODMwYzdkOGNmNTllMjk0Y2FiNTg5YzBmMmNiNjYwMTphYm9nZGFs")
#client = YouTrackClient('http://todo.bogdal.pl', username='abogdal', password='s2ymbfgg')


    


#cmd = {'redmine id': '33a', 'tag': 'test33', 'kwota': '33'}
cmd = "redmine id 33a &#9; tag test22"
print client.execute_command('test-50', cmd)

#fields = client.get_project_fields('test')
#for field in fields:
#    print field


#
#issues = client.get_project_issues('geo', query='timezone')
#for issue in issues:
#    print '*'*20
#    print issue['id']
#    print issue.find("field", {'name': 'State'}).text
#    print issue.find("field", {'name': 'Priority'}).text
#    print issue.find("field", {'name': 'summary'}).text
#    timestamp = issue.find("field", {'name': 'created'}).text
#    print datetime.fromtimestamp(float(timestamp) / 1e3)
#    #print issue.find("field", {'name': 'description'}).text
