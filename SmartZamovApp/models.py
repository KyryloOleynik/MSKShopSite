from django.db import models
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser

# Create your models here.
class Product_Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Product_Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=30)
    slug = models.SlugField(unique=True)
    description = RichTextField()
    price = models.DecimalField(max_digits=13, decimal_places=2)
    price_without_sale = models.DecimalField(max_digits=13, decimal_places=2)
    image = models.ImageField(upload_to='media/', blank=False, null=False)
    image2 = models.ImageField(upload_to='media/', blank=False, null=False)
    image3 = models.ImageField(upload_to='media/', blank=True, null=True)
    image4 = models.ImageField(upload_to='media/', blank=True, null=True)
    image5 = models.ImageField(upload_to='media/', blank=True, null=True)
    image6 = models.ImageField(upload_to='media/', blank=True, null=True)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', related_name='tags', blank=True)
    

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    user = models.ForeignKey('CustomUser', related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(max_length=40,  choices=[
        ('On cart', 'On cart'),
        ('Pending', 'Pending'),
        ('Waiting_for_payment', 'Waiting_for_payment'),
        ('Completed', 'Completed'),
        ('Active', 'Active'),
        ('Shipped', 'Shipped'),
        ('Canceled', 'Canceled'),
    ], default='on_cart')
    total = models.DecimalField(max_digits=13, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    order_adress = models.CharField(max_length=60, blank=True, null=True)
    delivery_method = models.CharField(max_length=40, choices=[
        ('Почта России (Россия)', 'Почта России (Россия)'),
        ('СДЭК (Россия)', 'СДЭК (Россия)'),
        ('Сourier (Only for Moscow and Berlin)', 'Сourier (Only for Moscow and Berlin)'),
        ('DHL (Europe)', 'DHL (Europe)'),
        ('UPS (Europe)', 'UPS (Europe)'),
    ], blank=True, null=True)
    payment_method = models.CharField(max_length=40, choices=[
        ('Cash on delivery', 'Cash on delivery'),
        ('On card', 'On card'),
        ('Crypto', 'Crypto'),
    ], blank=True, null=True)
    recipient_name = models.CharField(max_length=80, blank=False, null=True)
    is_paid = models.BooleanField(default=False)
    due_for_payment_now = models.DecimalField(max_digits=13, decimal_places=2, blank=True, null=True)

    @property
    def total(self):
        return sum(item.price for item in self.items.all()) 
        
    @property
    def total_without_sale(self):
        return sum(item.price_without_sale for item in self.items.all())

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_item', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def price(self):
        return self.quantity * self.product.price
        
    @property
    def price_without_sale(self):
        return self.quantity * self.product.price_without_sale

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=25, unique=True, blank=False, null=False)
    liked_products = models.ManyToManyField(Product, related_name="liked_products", blank=True)
    adress = models.CharField(max_length=60, blank=True, null=True)
    patronymic = models.CharField(max_length=60, blank=True, null=True)
    tg_id = models.CharField(max_length=60, blank=True, null=True)

    def count_unread_messages(self):
        return self.messages.filter(is_read=False).count()
        
    @property
    def initials(self):
        return self.last_name + " " + self.first_name + " " + self.patronymic
        
class BankCards(models.Model):
    card_number = models.CharField(max_length=16, unique=True, blank=False, null=False)
    card_expiry = models.CharField(max_length=7, help_text="MM / YY")
    card_cvv = models.CharField(max_length=3, blank=False, null=False) 
    card_owner = models.ForeignKey(CustomUser, related_name='owned_cards', on_delete=models.CASCADE)
    
    @property
    def card_owner_initials(self):
        return self.card_owner.initials

class ViewProd(models.Model):
    user = models.ForeignKey(CustomUser, related_name='viewed_products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='viewed_by_users', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    user = models.ForeignKey('CustomUser', related_name='messages', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='message_order', on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        self.is_read=True
        self.save()