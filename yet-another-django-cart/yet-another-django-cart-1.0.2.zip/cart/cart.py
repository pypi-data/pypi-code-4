import datetime
import models

class ItemAlreadyExists(Exception):
    pass

class ItemDoesNotExist(Exception):
    pass

class Cart:
    def __init__(self, request, session_key='MAIN_CART_ID'):
        self.session_key = session_key
        cart_id = request.session.get(self.session_key)
        if cart_id:
            try:
                cart = models.Cart.objects.get(id=cart_id, checked_out=False)
            except models.Cart.DoesNotExist:
                cart = self.new(request)
        else:
            cart = self.new(request)
        self.cart = cart

    def __iter__(self, **kwargs):
        self.get_items()

    def get_items(self, **kwargs):
        for item in self.cart.item_set.filter(**kwargs):
            yield item

    def new(self, request):
        cart = models.Cart(creation_date=datetime.datetime.now())
        cart.save()
        request.session[self.session_key] = cart.id
        return cart

    def add(self, product, unit_price, quantity=1, override_quantity=False, options=None):
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            item = models.Item()
            item.cart = self.cart
            item.product = product
            item.unit_price = unit_price
            item.quantity = quantity

            item.save()
            
            if options:
                item.options = options
        else: #ItemAlreadyExists

            if options:
                item.clear_options()
                item.options = options
                
            item.unit_price = unit_price
            item.quantity = quantity if override_quantity else item.quantity + int(quantity)
            item.save()

    def remove(self, product):
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            raise ItemDoesNotExist
        else:
            item.delete()

    def update(self, product, quantity, unit_price=None):
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            raise ItemDoesNotExist
            
    def count(self):
        result = 0
        for item in self.cart.item_set.all():
            result += 1 * item.quantity
        return result
        
    def summary(self):
        result = 0
        for item in self.cart.item_set.all():
            result += item.total_price
        return result

    def clear(self):
        for item in self.cart.item_set.all():
            item.delete()

