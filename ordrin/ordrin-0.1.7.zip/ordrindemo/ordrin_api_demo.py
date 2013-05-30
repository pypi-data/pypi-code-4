#! python
import datetime
import uuid
import functools
from pprint import pprint
import random
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

import ordrin
import ordrin.data
import ordrin.errors

#
# Helper Decorators
#
def print_docstring_header(f):
  @functools.wraps(f)
  def g(*args, **kwargs):
    print ''
    print f.__doc__
    raw_input('Press enter to execute and see the response')
    return f(*args, **kwargs)
  return g

def print_api_errors(f):
  @functools.wraps(f)
  def g(*args, **kwargs):
    try:
      return f(*args, **kwargs)
    except ordrin.errors.ApiError as e:
      print "The API returned the following error:"
      print e
  return g

#
# Global Variables
#
api_key = raw_input("Please input your API key: ")

api = ordrin.APIs(api_key, ordrin.TEST) # Create an API object

# Create an Address object
address = ordrin.data.Address('1 Main Street', 'College Station', 'TX', '77840', '(555) 555-5555')
address_nick = 'addr1'

# Create a CreditCard object
first_name = 'Test'
last_name = 'User'
credit_card = ordrin.data.CreditCard(first_name+' '+last_name, '01', str(datetime.date.today().year+2), address, '4111111111111111', '123')
credit_card_nick = 'cc1'

#Create a UserLogin object
unique_id = uuid.uuid1().hex
email = 'demo+{}@ordr.in'.format(unique_id)
password = 'password'
login = ordrin.data.UserLogin(email, password)
alt_first_name = 'Example'
alt_email = 'demo+{}alt@ordr.in'.format(unique_id)
alt_login = ordrin.data.UserLogin(alt_email, password)
new_password = 'password1'

#
# Restaurant demo functions
#
@print_docstring_header
def delivery_list_immediate_demo():
  """Get a list of restaurants that will deliver if you order now"""
  delivery_list_immediate = api.restaurant.get_delivery_list('ASAP', address)
  pprint(delivery_list_immediate, indent=4, depth=2)
  return delivery_list_immediate

@print_docstring_header
def delivery_list_future_demo():
  """Get a list of restaurants that will deliver if you order for 12 hours from now"""
  future_datetime = datetime.datetime.now() + datetime.timedelta(hours=12) #A timestamp twelve hours in the future
  delivery_list_later = api.restaurant.get_delivery_list(future_datetime, address)
  pprint(delivery_list_later, indent=4, depth=2)

@print_docstring_header
def delivery_check_demo(restaurant_id):
  """Get whether a particular restaurant will deliver if you order now"""
  delivery_check = api.restaurant.get_delivery_check(restaurant_id, 'ASAP', address)
  pprint(delivery_check, indent=4, depth=2)

@print_docstring_header
def fee_demo(restaurant_id):
  """Get fee and other info for ordering a given amount with a given tip"""
  subtotal = "$30.00"
  tip = "$5.00"
  fee_info = api.restaurant.get_fee(restaurant_id, subtotal, tip, 'ASAP', address)
  pprint(fee_info, indent=4, depth=2)

@print_docstring_header
def detail_demo(restaurant_id):
  """Get detailed information about a single restaurant"""
  restaurant_detail = api.restaurant.get_details(restaurant_id)
  pprint(restaurant_detail, indent=4, depth=3)
  return restaurant_detail

def find_deliverable_time(restaurant_id):
  """Find a time when this restaurant will deliver"""
  delivery_check = api.restaurant.get_delivery_check(restaurant_id, 'ASAP', address)
  delivery = delivery_check['delivery']
  if delivery:
    return 'ASAP'
  dt = datetime.datetime.now() + datetime.timedelta(hours=1)
  while not delivery:
    delivery_check = api.restaurant.get_delivery_check(restaurant_id, dt, address)
    delivery = delivery_check['delivery']
    dt += datetime.timedelta(hours=1)
  return dt
    
#
# User demo functions
#
@print_docstring_header
def get_user_demo():
  """Get information about a user"""
  user_info = api.user.get(login)
  pprint(user_info)

@print_docstring_header
def create_user_demo():
  """Create a user"""
  response = api.user.create(login, first_name, last_name)
  pprint(response)

@print_docstring_header
@print_api_errors
def update_user_demo():
  """Update a user"""
  response = api.user.update(login, alt_first_name, last_name)
  pprint(response)

@print_docstring_header
def get_all_addresses_demo():
  """Get a list of all saved addresses"""
  address_list = api.user.get_all_addresses(login)
  pprint(address_list)

@print_docstring_header
def get_address_demo():
  """Get an address by nickname"""
  addr = api.user.get_address(login, address_nick)
  pprint(addr)

@print_docstring_header
@print_api_errors
def set_address_demo():
  """Save an address with a nickname"""
  response = api.user.set_address(login, address_nick, address)
  pprint(response)

@print_docstring_header
@print_api_errors
def remove_address_demo():
  """Remove a saved address by nickname"""
  response = api.user.remove_address(login, address_nick)
  pprint(response)

@print_docstring_header
def get_all_credit_cards_demo():
  """Get a list of all saved credit cards"""
  credit_card_list = api.user.get_all_credit_cards(login)
  pprint(credit_card_list)

@print_docstring_header
def get_credit_card_demo():
  """Get a saved credit card by nickname"""
  credit_card = api.user.get_credit_card(login, credit_card_nick)
  pprint(credit_card)

@print_docstring_header
@print_api_errors
def set_credit_card_demo():
  """Save a credit card with a nickname"""
  response = api.user.set_credit_card(login, credit_card_nick, credit_card)
  pprint(response)

@print_docstring_header
@print_api_errors
def remove_credit_card_demo():
  """Remove a saved credit card by nickname"""
  response = api.user.remove_credit_card(login, credit_card_nick)
  pprint(response)

@print_docstring_header
def get_order_history_demo(login):
  """Get a list of all orders made by this user"""
  order_list = api.user.get_order_history(login)
  pprint(order_list)

@print_docstring_header
def get_order_detail_demo(oid):
  """Get the details of a particular order made by this user"""
  order_detail = api.user.get_order_detail(login, oid)
  pprint(order_detail)

@print_docstring_header
@print_api_errors
def set_password_demo():
  """Set a new password for a user"""
  response = api.user.set_password(login, new_password)
  pprint(response)
  
#
# Order demo functions
#
@print_docstring_header
@print_api_errors
def anonymous_order_demo(restaurant_id, tray, date_time):
  """Order food as someone without a user account"""
  tip = random.randint(0, 500)/100.0
  response = api.order.order(restaurant_id, tray, tip, date_time, first_name, last_name, address, credit_card, email=email)
  pprint(response)

@print_docstring_header
@print_api_errors
def create_user_and_order_demo(restaurant_id, tray, date_time):
  """Order food and create an account"""
  tip = random.randint(0, 500)/100.0
  response = api.order.order_create_user(restaurant_id, tray, tip, date_time, first_name, last_name, address, credit_card, alt_email, password)
  pprint(response)

@print_docstring_header
@print_api_errors
def order_with_nicks_demo(restaurant_id, tray, date_time):
  """Order food as a logged in user using previously stored address and credit card"""
  tip = random.randint(0, 500)/100.0
  response = api.order.order(restaurant_id, tray, tip, date_time, first_name, last_name, address_nick, credit_card_nick, login=login)
  pprint(response)
  return response

def find_item_to_order(item_list):
  for item in item_list:
    if item['is_orderable']:
      if float(item['price'])>=5.00:
        return item['id']
    else:
      if 'children' in item:
        item_id = find_item_to_order(item['children'])
        if item_id is not None:
          return item_id
  return None
    

#
# Main
#
def run_demo():
  """Run through the entire demo sequence"""
  # Restaurant functions
  delivery_list = delivery_list_immediate_demo()
  delivery_list_future_demo()
  restaurant_id = delivery_list[0]['id']
  delivery_check_demo(restaurant_id)
  fee_demo(restaurant_id)
  detail = detail_demo(restaurant_id)

  # User functions
  create_user_demo()
  get_user_demo()
  update_user_demo()
  get_user_demo()
  set_address_demo()
  get_address_demo()
  set_credit_card_demo()
  get_credit_card_demo()

  # Order functions
  order_date_time = find_deliverable_time(restaurant_id)
  print "Ordering food at {}".format(order_date_time)
  item_id = find_item_to_order(detail['menu'])
  item = ordrin.data.TrayItem(item_id, quantity=10)
  tray = ordrin.data.Tray(item)
  anonymous_order_demo(restaurant_id, tray, order_date_time)
  order = order_with_nicks_demo(restaurant_id, tray, order_date_time)
  if order:
    get_order_detail_demo(order['refnum'])

  create_user_and_order_demo(restaurant_id, tray, order_date_time)
  get_order_history_demo(alt_login)

  # Clean up/removing stuff
  remove_address_demo()
  get_all_addresses_demo()
  remove_credit_card_demo()
  get_all_credit_cards_demo()
  set_password_demo()
  #After changing the password I must change the login object to continue to access user info

if __name__=='__main__':
  run_demo()
  
