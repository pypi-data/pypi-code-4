import unittest
import airbrite
import airbrite.api

CURRENT_END_POINT = 'https://api.airbrite.io/v2/'


class ConnectionTestCase(unittest.TestCase):

    def test_defaults_to_test_API_KEY(self):
        self.assertEqual(airbrite.API_KEY, airbrite.TEST_API_KEY)

    def test_endpoint(self):
        self.assertEqual(airbrite.END_POINT, CURRENT_END_POINT)

    def test_can_connect(self):
        ret = airbrite.test_connection()
        self.assertTrue(ret)


class ProductTestCase(unittest.TestCase):
    """Test the actual Product, not its REST endpoint functionality"""

    DATA = {
        u'_id': u'5237a50459459f0500000007',
        u'created': 1379378436,
        u'created_date': u'2013-09-17T00:40:36.649Z',
        u'description': u'My First Product',
        u'inventory': None,
        u'metadata': {},
        u'name': None,
        u'sku': u'first-product',
        u'updated': 1379378436,
        u'updated_date': u'2013-09-17T00:40:36.649Z',
        u'user_id': u'5237a347429acf0400000013',
        u'weight': None
    }

    MY_FIRST_PRODUCT_ID = u'5237a50459459f0500000007'

    def test_instance_id(self):
        product = airbrite.api.Product()
        product._from_data(self.DATA)
        self.assertEqual(product._id, self.MY_FIRST_PRODUCT_ID)


class RESTProductTestCase(unittest.TestCase):
    """Test the 'products' frontend to the REST interface"""

    MY_FIRST_PRODUCT_ID = u'5237a50459459f0500000007'

    def test_get_product(self):
        product = airbrite.get_product(self.MY_FIRST_PRODUCT_ID)
        self.assertIsInstance(product, airbrite.api.Product)
        self.assertEqual(product._id, self.MY_FIRST_PRODUCT_ID)

    def test_get_products(self):
        products = airbrite.get_products()
        self.assertIsNotNone(products)
        self.assertTrue(hasattr(products, 'next'))

    def test_get_products_test_all(self):
        # len() is not yet supported, so we exhaust the iterator.
        products = airbrite.get_products()
        ps = []
        first_product = None
        for product in products:
            ps.append(product)
            if product._id == self.MY_FIRST_PRODUCT_ID:
                first_product = product

        self.assertTrue(len(ps) > 0)
        self.assertIsInstance(first_product, airbrite.api.Product)


class OrderTestCase(unittest.TestCase):
    """Test the actual Order, not its REST endpoint functionality"""

    ORDERED_PRODUCT = {
        u'_id': u'5237a50459459f0500000007',
        u'description': u'My First Product',
        u'sku': u'first-product',
    }

    ORDER_DATA = {
        u'_id': u'524c2c11890bc60500000001',
        u'created': 1380723729,
        u'created_date': u'2013-10-02T14:22:09.504Z',
        u'currency': u'usd',
        u'customer_id': None,
        u'description': None,
        u'discount': {},
        u'line_items': [{u'description': u'My First Product',
                         u'inventory': None,
                         u'metadata': {},
                         u'name': None,
                         u'quantity': 1,
                         u'sku': u'first-product',
                         u'updated': 1379378436,
                         u'updated_date': u'2013-09-17T00:40:36.649Z',
                         u'weight': None}],
        u'metadata': {},
        u'order_number': 1028,
        u'shipping': {},
        u'shipping_address': None,
        u'status': None,
        u'tax': {},
        u'updated': 1380723729,
        u'updated_date': u'2013-10-02T14:22:09.505Z',
        u'user_id': u'5237a347429acf0400000013'
    }

    def test_order(self):
        order = airbrite.api.Order()
        self.assertTrue(order, '_id')

    def test_order_with_data(self):
        order = airbrite.api.Order(data=self.ORDER_DATA)
        self.assertEqual(order._id, self.ORDER_DATA['_id'])
        self.assertEqual(len(order.line_items), 1)


class RESTOrderTestCase(unittest.TestCase):
    """Test the 'orders' frontend to the REST interface"""

    ORDER_SKU = 'first-product'
    ORDER_QUANTITY = 1
    STRIPE_CARD_TOKEN = 'tok_2gDluFcLl1UEXV'

    def test_new_order_only_sku(self):
        self.assertRaises(ValueError, airbrite.new_order, sku=self.ORDER_SKU)

    def test_new_order_only_quantity(self):
        self.assertRaises(ValueError, airbrite.new_order, quantity=1)

    def test_new_order_with_sku_and_quantity(self):
        order = airbrite.new_order(sku=self.ORDER_SKU,
                                   quantity=self.ORDER_QUANTITY)
        self.assertIsInstance(order, airbrite.api.Order)
        self.assertEqual(order.quantity, self.ORDER_QUANTITY)
        self.assertEqual(order.line_items[0]['sku'], self.ORDER_SKU)

    def test_new_order_with_line_items(self):
        item = {
            'sku': self.ORDER_SKU,
            'quantity': self.ORDER_QUANTITY,
        }
        order = airbrite.new_order(line_items=[item])
        self.assertIsInstance(order, airbrite.api.Order)
        self.assertEqual(order.quantity, self.ORDER_QUANTITY)
        self.assertEqual(order.line_items[0]['sku'], self.ORDER_SKU)


class PaymentTestCase(unittest.TestCase):

    AMOUNT = 100
    CARD_TOKEN = 'tok_xxxxxxxxxxxxxxx'

    def test_payment_no_card_token(self):
        self.assertRaises(ValueError, airbrite.payment, amount=self.AMOUNT)

    def test_payment_no_amount(self):
        self.assertRaises(ValueError, airbrite.payment,
                          card_token=self.CARD_TOKEN)

    def test_payment_minimum_params(self):
        payment = airbrite.payment(amount=self.AMOUNT,
                                   card_token=self.CARD_TOKEN)
        self.assertEqual(payment['amount'], self.AMOUNT)
        self.assertEqual(payment['card_token'], self.CARD_TOKEN)
        # Defaults
        self.assertEqual(payment['gateway'], 'stripe')
        self.assertEqual(payment['currency'], 'usd')

    def test_payment(self):
        payment = airbrite.payment(amount=self.AMOUNT,
                                   card_token=self.CARD_TOKEN,
                                   currency='ar',
                                   gateway='ultra-stripe')
        self.assertEqual(payment['amount'], self.AMOUNT)
        self.assertEqual(payment['card_token'], self.CARD_TOKEN)
        # added parameters
        self.assertEqual(payment['gateway'], 'ultra-stripe')
        self.assertEqual(payment['currency'], 'ar')
