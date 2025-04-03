from modeltranslation.translator import translator, TranslationOptions
from .models import Product_Category, Product, Message, Tag, Order

class TagTranslationOption(TranslationOptions):
    fields = ('name',)

translator.register(Tag, TagTranslationOption)

class MessageTranslationOption(TranslationOptions):
    fields = ('text', )

translator.register(Message, MessageTranslationOption)

class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'price', 'price_without_sale')

translator.register(Product, ProductTranslationOptions)

class ProductCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Product_Category, ProductCategoryTranslationOptions)

class OrderTranslationOptions(TranslationOptions):
    fields = ('due_for_payment_now',)

translator.register(Order, OrderTranslationOptions)