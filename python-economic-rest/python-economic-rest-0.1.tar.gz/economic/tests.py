from economic.auth import Authentication
from economic.customers import Customer
from economic.employees import Employee
from economic.invoices import BookedInvoice, DraftInvoice
from economic.products import Product

APP_ID = "IfE9Qz5zj1zi9fpv5YBnwo_B7Z9lNUzLlTnjvCEOgj41"
ACCESS_ID = "PJoGSJMhokWjUbcXhA3B_oilu8y1LsNO-uHLBovrFmI1"

auth = Authentication(APP_ID, ACCESS_ID)

#print Employee.all(auth)
for invoice in BookedInvoice.all(auth):
    print invoice, invoice.get_our_reference()
#print DraftInvoice.all(auth)
#print Customer.all(auth)
#print Product.all(auth)