from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Product, Product_Category, Order, OrderItem, Message, ViewProd, Tag, BankCards
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils.timezone import localtime
from datetime import timedelta
# Register your models here.
@admin.register(BankCards)
class AdminBankCards(admin.ModelAdmin):
    list_display = ('card_number', 'card_owner_initials',)

@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ViewProd)
class AdminViewProd(admin.ModelAdmin):
    readonly_fields = ('formatted_created',)

    def formatted_created(self, obj):
        return self.format_datetime_field(obj.created)
    formatted_created.short_description = "Дата просмотра"
    
    def format_datetime_field(self, dt):
        if not dt:
            return "-"
        
        local_dt = localtime(dt)

        date_str = local_dt.strftime("%d.%m.%Y")
        time_str = local_dt.strftime("%H:%M:%S")

        return format_html(
            '<div>'
            '<b>Дата:</b> <input type="text" value="{}" readonly style="border: none; background: transparent;"> '
            '<span style="margin-left: 4.5%;">📅</span><br>'
            '<b>Время:</b> <input type="text" value="{}" readonly style="border: none; background: transparent;"> '
            '<span>⏳</span><br>'
            '</div>',
            date_str, time_str
        )
    
    list_display = ('user', 'product', 'created')
    ordering = ('-created',)
    list_filter = ('created', 'user', 'created')

@admin.register(Message)
class AdminMessage(admin.ModelAdmin):
    list_display = ('user', 'order', 'text')

@admin.register(Order)
class AdminOrder(admin.ModelAdmin):
    list_display = ('user', 'status', 'total', 'created', 'order_adress', 'payment_method', 'delivery_method', 'is_paid', 'due_for_payment_now')
    list_filter = ('status', 'created', 'due_for_payment_now')

@admin.register(OrderItem)
class AdminOrderItem(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    list_filter = ('quantity', )

@admin.register(Product_Category)
class AdminProduct_Category(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available', 'created', 'brand', 'price_without_sale')
    list_filter = ('available', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'available')

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (_('Номер телефону'), {'fields': ('phone_number',)}),
        (_('Адрес користувача'), {'fields': ('adress',)}),
        (_('По батькові користувача'), {'fields': ('patronymic',)}),
        (_('Id користувача в Телеграм'), {'fields': ('tg_id',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Номер телефону'), {'fields': ('phone_number',)}),
        (_('Id користувача в Телеграм'), {'fields': ('tg_id',)}),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff', 'adress', 'patronymic', 'tg_id')

admin.site.register(CustomUser, CustomUserAdmin)