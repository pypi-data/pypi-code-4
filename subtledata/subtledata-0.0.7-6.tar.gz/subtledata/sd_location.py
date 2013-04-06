__author__ = 'gsibble'

from base_types import  SDFirstClassObject
from sd_menu import SDMenu
from sd_table import SDTable
from sd_collections_tables import SDTableCollection

class SDLocation(SDFirstClassObject):

    def __init__(self, parent, location_id, include_menu=False, use_cache=True, fetch=True, initial_data=None, *args, **kwargs):
        super(SDLocation, self).__init__(parent, use_cache)
        self._location_id = location_id
        self._include_menu = include_menu

        if fetch:
            self.refresh()
        else:
            if initial_data:
                self._set_attribs(initial_data)


    def refresh(self):
        #Get the location via swagger
        self._swagger_location = self._swagger_locations_api.getLocation(self._location_id, self._api_key,
                                                                         use_cache=self._use_cache)

        #Set attributes of first class Location to match Swagger Location object
        self._set_attribs(self._swagger_location)

        if self._include_menu:
            self.update_menu(self._use_cache)

    @property
    def tables(self):
        self._swagger_tables = self._swagger_locations_api.getTableList(location_id=self._location_id, api_key=self._api_key)

        #Set the tables to be our type
        table_list = [SDTable(self, table) for table in self._swagger_tables]

        return SDTableCollection(tables=table_list, parent=self)

    def update_menu(self, use_cache=True):

        if not self._use_cache:
            use_cache = False

        self._swagger_menu = self._swagger_locations_api.getLocationMenu(self._location_id, self._api_key,
                                                                         use_cache=use_cache)

    @property
    def menu(self):

        if not hasattr(self, '_swagger_menu'):
            self.update_menu()

        return SDMenu(self, self._swagger_menu)

    @property
    def open_tables(self):
        return []

    def open_ticket_for_dine_in(self, user_id, device_id, table_id, business_expense=False):
        new_ticket_body = {

        }

        #TODO:  Implement Later
        #Return a SDTicket
        pass

    def open_ticket_for_take_out(self, user_id):

        #Return a SDTicket
        pass

    def open_ticket_for_delivery(self, user_id):

        #Return a SDTicket
        pass

    @property
    def tickets(self):
        return None