# TODO: define a manager to handle paging for the resources.


class Product (object):

    def __init__(self, data={}):
        self._id = ''
        self.name = ''
        self.description = ''
        self.inventory = None
        self.metadata = {}
        self.weight = None

        self.created = 0
        self.updated = 0
        # TODO: This should be datetime objects
        self.created_date = ''
        self.updated_date = ''

        self.user_id = ''

        if data:
            self._from_data(data)

    def _from_data(self, data):
        """Initialize the Product instance with the data dict"""
        self._id = data[u'_id'] if u'_id' in data else self._id
        self.name = data[u'name'] if u'name' in data else self.name
        self.sku = data[u'sku'] if u'sku' in data else self.sku
        self.description = data[u'description'] if u'description' in data else self.description
        self.inventory = data[u'inventory'] if u'inventory' in data else self.inventory
        self.metadata = data[u'metadata'] if u'metadata' in data else self.metadata
        self.weight = data[u'weight'] if u'weight' in data else self.weight

        self.created = data[u'created'] if u'created' in data else self.created
        self.updated = data[u'updated'] if u'updated' in data else self.updated
        # TODO: This should be datetime objects
        self.created_date = data[u'created_date'] if u'created_date' in data else self.created_date
        self.updated_date = data[u'updated_date'] if u'updated_date' in data else self.updated_date

        self.user_id = data[u'user_id'] if u'user_id' in data else self.user_id

        # TODO: reimplement __repr__ and __str__ to avoid this reference
        self._data = data

    def __repr__(self):
        return "<Product (%s)>" % str(self._id)

    def __str__(self):
        # TODO: make it more user-friendly.
        return repr(self.to_dict())

    def to_dict(self):
        return self._data

###############################################################################


class Order (object):

    def __init__(self, data={}):
        self._id = ''
        self.user_id = ''
        self.customer_id = None
        self.order_number = 0
        self.description = ''

        self.currency = ''
        self.discount = {}
        self.tax = {}

        self.shipping = {}
        self.shipping_address = None
        self.status = None

        self.created = 0
        self.updated = 0
        # TODO: This should be datetime objects
        self.created_date = ''
        self.updated_date = ''

        self.metadata = {}
        self.line_items = []
        self.status = None

        if data:
            self._from_data(data)

    def _from_data(self, data):
        """Initialize the Product instance with the data dict"""
        self._id = data[u'_id'] if '_id' in data else self._id
        self.user_id = data[u'user_id'] if u'user_id' in data else self.user_id
        self.customer_id = data[u'customer_id'] if u'customer_id' in data else self.customer_id
        self.order_number = data[u'order_number'] if u'order_number' in data else self.order_number
        self.description = data[u'description'] if u'description' in data else self.description

        self.currency = data[u'currency'] if u'currency' in data else self.currency
        self.discount = data[u'discount'] if u'discount' in data else self.discount
        self.tax = data[u'tax'] if u'tax' in data else self.tax

        self.shipping = data[u'shipping'] if u'shipping' in data else self.shipping
        self.shipping_address = data[u'shipping_address'] if u'shipping_address' in data else self.shipping_address
        self.status = data[u'status'] if u'status' in data else self.status

        self.created = data[u'created'] if u'created' in data else self.created
        self.updated = data[u'updated'] if u'updated' in data else self.updated
        # TODO: This should be datetime objects
        self.created_date = data[u'created_date'] if u'created_date' in data else self.created_date
        self.updated_date = data[u'updated_date'] if u'updated_date' in data else self.updated_date

        self.metadata = data[u'metadata'] if u'metadata' in data else self.metadata

        # TODO: make this Product instances, or at least Product proxies
        self.line_items = data[u'line_items'] if u'line_items' in data else self.line_items

        self.status = data[u'status'] if u'status' in data else self.status

        # TODO: reimplement __repr__ and __str__ to avoid this reference
        self._data = data

    @property
    def quantity(self):
        return len(self.line_items)

    def __repr__(self):
        return "<Order (%s)>" % str(self._id)

    def __str__(self):
        # TODO: make it more user-friendly.
        return repr(self.to_dict())

    def to_dict(self):
        return self._data
