from renren import RenrenAutoAuth

#api = RenrenAutoAuth(0, '11a114ee1bf74aaca9823505b415be8a','42f2cbb060c4d19bc0c5be651743711','https://snsapi.ie.cuhk.edu.hk/aux/auth.php','hupili.renren1@gmail.com','myrenrenacc')
api = RenrenAutoAuth(0, 'e7546498e7ec49808ca5a45f43186343','e153a11fbcbb452e93e2455dfa4ea843','http://www.snsapi.sinaapp.com/?','hupili.renren1@gmail.com','myrenrenacc')
print api.get_authorize_url()
print api.get_code()

print api.get_access_token()

#"user_id": "", 
#"channel_name": "renren_account_1", 
#"auth_info": {
#"save_token_file": "(default)", 
#"cmd_request_url": "(dummy)", 
#"callback_url": "https://snsapi.ie.cuhk.edu.hk/aux/auth.php", 
#    "cmd_fetch_code": "(local_username_password)" 
#        }, 
#"app_secret": "742f2cbb060c4d19bc0c5be651743711", 
#"open": "yes", 
#"app_key": "11a114ee1bf74aaca9823505b415be8a"

