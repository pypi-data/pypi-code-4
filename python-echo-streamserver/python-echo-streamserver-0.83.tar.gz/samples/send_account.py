from  echo.core_api import send_request, Account

import logging
logging.getLogger().setLevel(logging.DEBUG)

# Non-default account: Must be Account.BasicAuth with no secret!
other_account=Account('test.echoenabled.com', '', Account.BasicAuth)

sample_value = { 'eat': 'me', 'ok': 1 }

# KVS Put a value:
print send_request('kvs/put', param_d={ 'appkey':'test.echoenabled.com',
             'key':'sample', 'value': sample_value }, http_post=True,
             account=other_account)

# KVS Get that value:
print send_request('kvs/get', param_d={ 'appkey':'test.echoenabled.com',
             'key':'sample' }, account=other_account)

