from fullcontact import FullContact
import requests
import divan

def get_identity(config, email):
  fc = FullContact(config['FC_KEY'])

  db = divan.Database(config['DB_URI'],
                        config['DB_NAME'],
                        auth=(config['DB_USER'],
                              config['DB_PASS']))
  try:
    res = db.get_or_create()
    assert res.status_code in [200, 201]
  except AssertionError:
    return res.status_code, res.json()
  else:
    res = db.get(email)
    if res.status_code == 200:
      return res.status_code, res.json()
    else:
      profile = fc.get(email=email)
      profile['_id'] = email
      res = db.post(params=profile)
      return res.status_code, profile