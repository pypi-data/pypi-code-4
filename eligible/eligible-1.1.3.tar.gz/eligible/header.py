import eligible
import os, sys, json

ua = {
      'bindings_version':eligible.api_version,
      'lang':'python',
      'lang_version':sys.version.splitlines()[0],
      'platform':sys.version.splitlines()[1],
      'publisher':'eligible',
      'uname':','.join(os.uname())
     }

headers = {
           'x-eligible-client-user-agent':json.dumps(ua),
           'user_agent':'Eligible/v1 PythonBindings/{}'.format(eligible.api_version),
           'authorization':'Bearer {}'.format(eligible.api_key),
           'content_type':'application/x-www-form-urlencoded',
           'eligible_version':eligible.api_version
          }
