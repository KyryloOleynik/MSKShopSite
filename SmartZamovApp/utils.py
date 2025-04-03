from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
import SmartZamovProj.settings as settings
from decimal import Decimal
from django.conf import settings
from .models import Product 
from django.utils import timezone
from collections import OrderedDict
import json, copy

class Viewed:
    def __init__(self, request):
        self.session = request.session
        viewed_products = self.session.get(settings.VIEW_SESSION_ID)
        if not viewed_products:
            viewed_products = self.session[settings.VIEW_SESSION_ID] = {}
        self.viewed_products = viewed_products
    
    def add_product(self, product, time=None):
        if time is None:
            time = timezone.now()
        time_str = time.isoformat()
        product_id = product.id
        self.viewed_products[product_id] = {'add_time': time_str}
        self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session.pop(settings.VIEW_SESSION_ID, None)
        self.save()

    def __iter__(self):
        products_ids = list(self.viewed_products.keys())
        products_ids.sort(key=lambda x: self.viewed_products[x]['add_time'], reverse=True)        
        for product_id in products_ids:
            yield Product.objects.get(id=product_id)

    def default_iter(self):      
        viewed_products = OrderedDict(sorted(self.viewed_products.items(), key=lambda x: x[1]['add_time'], reverse=True))

        products_ids = list(viewed_products.keys())
        products = {p.id: p for p in Product.objects.filter(id__in=products_ids)}

        for viewed_product, prod_data in viewed_products.items():
            prod_data['item'] = products.get(int(viewed_product))
            yield prod_data

    def count(self):
        return len(self.viewed_products)
    
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def save(self):
        self.session.modified = True
    
    def add(self, product, quantity=1, resetQuantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price), 'price_without_sale': str(product.price_without_sale)}
        if resetQuantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()
    
    def remove(self, product, quantity=1, remove_all=True):
        product_id = str(product.id)
        if product_id in self.cart.keys():
            if remove_all:
                del self.cart[product_id]
            else:
                self.cart[product_id]['quantity'] -= quantity 
                if self.cart[product_id]['quantity'] < 1: 
                    del self.cart[product_id]
            self.save()
    
    def clear(self):
        self.session.pop(settings.CART_SESSION_ID, None)
        self.save()

    def __iter__(self):
        products_ids = self.cart.keys()
        products = Product.objects.filter(id__in=products_ids)
        cart = copy.deepcopy(self.cart)
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] =  item['price'] * item['quantity']
            yield item
    
    def count(self):
        return len(self.cart)
    
    def get_total_price(self):
        return sum(Decimal(product['price']) * product['quantity'] for product in self.cart.values())
    
    def get_total_price_without_sale(self):
        return sum(Decimal(product['price_without_sale']) * product['quantity'] for product in self.cart.values())    
        
def send_activation_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())
    domain = get_current_site(request).domain
    activation_link = f"https://{domain}/accounts/{uid}/{token}/activate/"
    subject = _('Activate your account')
    message = render_to_string('activation_email.html', {
        'user': user,
        'activation_link': activation_link,
    })
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])