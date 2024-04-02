from decimal import Decimal
from shop.models import ProductProxy


class Cart():

    def __init__(self, request) -> None:

        self.sesson = request.session
        cart = self.sesson.get('session_key')

        if not cart:
            cart = self.sesson['session_key'] = {}

        self.cart = cart

    def __len__(self):
        return sum(item['qty'] for item in self.cart.values())

    def __iter__(self):
        product_ids = self.cart.keys()
        products = ProductProxy.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total'] = item['price'] * item['qty']
            yield item

    def add(self, product, quantity):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'qty': quantity, 'price': str(product.price)}
        self.cart[product_id]['qty'] = quantity
        self.sesson.modified = True

    def delete(self, product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self.sesson.modified = True

    def update(self, product, quantity):
        product_id = str(product)
        if product_id in self.cart:
            self.cart[product_id]['qty'] = quantity
            self.sesson.modified = True

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['qty'] for item in self.cart.values())
