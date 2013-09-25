import xml.etree.cElementTree as ET
from .utils import KunakiElement, KunakiRequest


class ShippingProduct(KunakiElement):
    """ Kunaki Product. Used in Shipping Options and Order requests.
    """
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity

    def get_tree(self):
        """ Builds tree structure for the Product.
        """
        product = ET.Element('Product')
        ET.SubElement(product, 'ProductId').text = unicode(self.product_id)
        ET.SubElement(product, 'Quantity').text = unicode(self.quantity)
        return product


class ShippingOption(KunakiElement):
    """ Kunaki Shipping Option. Used for Shipping Options response.
    """
    def __init__(self, description, delivery_time, price):
        self.description = description
        self.delivery_time = delivery_time
        self.price = price

    def get_tree(self):
        """ Builds tree structure for the Shipping Option.
        """
        opt = ET.Element('Option')
        ET.SubElement(opt, 'Description').text = unicode(self.description)
        ET.SubElement(opt, 'DeliveryTime').text = unicode(self.delivery_time)
        ET.SubElement(opt, 'Price').text = unicode(self.price)
        return opt


class ShippingOptions(KunakiRequest):
    """ Kunaki Shipping Options request.
    """
    def __init__(self, country, state, postal_code, products, *args, **kwargs):
        super(ShippingOptions, self).__init__(*args, **kwargs)
        self.country = country
        self.state = state
        self.postal_code = postal_code
        self.products = products

    def get_tree(self):
        """ Builds tree structure for the Shipping Options.
        """
        options = ET.Element('ShippingOptions')
        ET.SubElement(options, 'Country').text = unicode(self.country)
        ET.SubElement(options, 'State_Province').text = unicode(self.state)
        ET.SubElement(options, 'PostalCode').text = unicode(self.postal_code)
        for product in self.products:
            options.append(product.get_tree())
        return options

    def get_options(self):
        """ Returns ShippingOption list retrieved from Kunaki
        """
        assert self.response is not None
        options = []
        for opt in self.response.findall('Option'):
            shipping_opt = ShippingOption(
                description=opt.find('Description').text,
                delivery_time=opt.find('DeliveryTime').text,
                price=opt.find('Price').text,
            )
            options.append(shipping_opt)
        return options

    def add_product(self, product):
        """ Adds a Kunaki Product to the Shipping Options `products` list.
        Expects `product` to be a ShippingProduct instance.
        """
        self.products.append(product)


class Order(KunakiRequest):
    """ Kunaki Order request.
    """
    def __init__(self, username, password, name, address1, city, postal_code,
                 country, shipping_description, products, state='',
                 address2='', company='', mode='Live', *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self.username = username
        self.password = password
        self.name = name
        self.address1 = address1
        self.city = city
        self.postal_code = postal_code
        self.country = country
        self.shipping_description = shipping_description
        self.products = products
        self.state = state
        self.address2 = address2
        self.company = company
        self.mode = mode

    def get_tree(self):
        """ Builds tree structure for the Order.
        """
        order = ET.Element('Order')
        ET.SubElement(order, 'UserId').text = unicode(self.username)
        ET.SubElement(order, 'Password').text = unicode(self.password)
        ET.SubElement(order, 'Mode').text = unicode(self.mode)
        ET.SubElement(order, 'Name').text = unicode(self.name)
        ET.SubElement(order, 'Company').text = unicode(self.company)
        ET.SubElement(order, 'Address1').text = unicode(self.address1)
        ET.SubElement(order, 'Address2').text = unicode(self.address2)
        ET.SubElement(order, 'City').text = unicode(self.city)
        ET.SubElement(order, 'State_Province').text = unicode(self.state)
        ET.SubElement(order, 'PostalCode').text = unicode(self.postal_code)
        ET.SubElement(order, 'Country').text = unicode(self.country)
        sd_elem = ET.SubElement(order, 'ShippingDescription')
        sd_elem.text = unicode(self.shipping_description)
        for product in self.products:
            order.append(product.get_tree())
        return order

    def add_product(self, product):
        """ Adds a Kunaki Product to the Order `products` list.
        Expects `product` to be a ShippingProduct instance.
        """
        self.products.append(product)

    @property
    def order_id(self):
        """ Returns the order id from the Kunaki Order response.
        """
        assert self.response is not None
        return self.response.find('OrderId').text


class OrderStatus(KunakiRequest):
    """ Kunaki Order Status request.
    """
    def __init__(self, username, password, order_id, *args, **kwargs):
        super(OrderStatus, self).__init__(*args, **kwargs)
        self.username = username
        self.password = password
        self.order_id = order_id

    def get_tree(self):
        """ Builds tree structure for the Order Status.
        """
        order_status = ET.Element('OrderStatus')
        ET.SubElement(order_status, 'UserId').text = unicode(self.username)
        ET.SubElement(order_status, 'Password').text = unicode(self.password)
        ET.SubElement(order_status, 'OrderId').text = unicode(self.order_id)
        return order_status

    @property
    def status(self):
        """ Returns the status from the Order Status response.
        """
        assert self.response is not None
        return self.response.find('OrderStatus').text

    @property
    def tracking_type(self):
        """ Returns the tracking type from the Order Status response.
        """
        assert self.response is not None
        return self.response.find('TrackingType').text

    @property
    def tracking_id(self):
        """ Returns the tracking id from the Order Status response.
        """
        assert self.response is not None
        return self.response.find('TrackingId').text
