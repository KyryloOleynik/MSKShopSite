from django import forms
from .models import CustomUser, Product, Product_Category, Order
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.backends import BaseBackend
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class FavoriteProductsForm(forms.Form):
    product_ids = forms.ModelMultipleChoiceField(queryset=Product.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

class ChangeUserData(forms.ModelForm):
    username = forms.CharField(label=_("Нікнейм: "), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Введіть імя користувача')}))    
    email = forms.EmailField(label=_("Електронна пошта: "), required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Введіть електронну пошту')}))    
    first_name = forms.CharField(label=_("Ім'я користувача: "), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Введіть ваше ім'я")}))    
    last_name = forms.CharField(label=_("Фамілія користувача: "), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':  _("Введіть вашу фамілію")}))    
    patronymic = forms.CharField(label=_("По батькові: "), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':  _("По батькові")}))    
    phone_number = forms.CharField(label=_("Номер телефону: "), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Введіть ваш номер телефону")}))    
    adress = forms.CharField(label=_("Адреса (Область, місто, вулиця): "),required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Введіть вашу адрессу")}))

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            return first_name
        if not first_name.isalpha():
            raise(ValidationError(_("Ім'я не повинно містити цифр")))
        if len(first_name) < 2:
            raise(ValidationError(_("Ім'я занадто коротке")))
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name:
            return last_name
        if not last_name.isalpha():
            raise(ValidationError(_("Фамілія не повинна містити цифр")))
        if len(last_name) < 2:
            raise(ValidationError(_("Фамілія занадто коротка")))
        return last_name
    
    def clean_patronymic(self):
        patronymic = self.cleaned_data['patronymic']
        if not patronymic:
            return patronymic
        if not patronymic.isalpha():
            raise(ValidationError(_("По батькові не повинно містити цифр")))
        if len(patronymic) < 2:
            raise(ValidationError(_("По батькові занадто коротке")))
        return patronymic
        
    def clean_adress(self):
        adress = self.cleaned_data['adress']
        if not adress:
            return adress
        parts = [part.strip() for part in adress.split(",")]
        if len(parts) != 3:
            raise ValidationError(_("Будь ласка, введіть адресу у вказаному форматі"))
        for part in parts:
            if len(part) < 4 or not part.isalpha():
                raise ValidationError(_("Будь ласка, введіть коректну адресу"))
        return adress
        
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'patronymic', 'phone_number', 'adress')

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label=_('Електронна пошта'), max_length=254, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Введіть електронну пошту')}))
    password1 = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Введіть пароль')}))
    password2 = forms.CharField(label=_('Підтвердження паролю'), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Підтвердіть пароль')}))
    username = forms.CharField(label=_("Никнейм користувача"), widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Введіть імя користувача')}))
    phone_number = forms.CharField(label=_("Номер телефону"), widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Введіть номер телефону')}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'phone_number')

    def clean_phone(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number):
            raise ValidationError(_('Користувач з таким номером телефону вже існує'))
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_('Користувач з таким email вже існує'))
        return email

class UserLoginBackend(BaseBackend):
    def authenticate(self, request, username = None, password = None, **kwargs):
        try:
            user = CustomUser.objects.get(email = username)
            if(user.check_password(password)):
                return user
        except:
            return None
        
    def get_user(self, user_id):
        try:
           return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
           return None
    
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label=_('Електронна пошта'), widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Введіть вашу електронну пошту')}))
    password = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Введіть ваш пароль')}))

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label=_('Старий пароль'), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Введіть старий пароль')}))
    new_password1 = forms.CharField(label=_('Новий пароль'), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Введіть новий пароль')}))
    new_password2 = forms.CharField(label=_('Підтвердіть новий пароль'), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Підтвердіть новий пароль')}))

class ResetPasswordForm(PasswordResetForm):
    email = forms.EmailField(label=_('Електронна пошта'), max_length=254, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Введіть електронну пошту')}))

class PlaceOrder(forms.ModelForm):
    phone_number = forms.CharField(
        label=_("Номер телефону"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 999-99-99'})
    )

    first_name = forms.CharField(
        label=_("Ім'я отримувача"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Іван')})
    )

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha():
            raise ValidationError(_("Ім'я повинно містити лише літери"))
        if len(first_name) < 2:
            raise ValidationError(_("Ім'я повинно бути не менше 2 символів"))
        return first_name

    last_name = forms.CharField(
        label=_("Прізвище отримувача"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Іванов')})
    )

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha():
            raise ValidationError(_("Прізвище повинно містити лише літери"))
        if len(last_name) < 2:
            raise ValidationError(_("Прізвище повинно бути не менше 2 символів"))
        return last_name

    patronymic = forms.CharField(
        label=_("По батькові отримувача"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Іванович')})
    )

    def clean_patronymic(self):
        patronymic = self.cleaned_data.get('patronymic')
        if not patronymic.isalpha():
            raise ValidationError(_("По батькові повинно містити лише літери"))
        return patronymic

    order_adress = forms.CharField(
        label=_("Адреса (Область, місто, вулиця): "),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Самарская область, Самара, ул. Ленина')})
    )

    def clean_order_adress(self):
        order_adress = self.cleaned_data['order_adress']
        if not order_adress:
            raise ValidationError(_("Адреса не може бути порожньою"))
        parts = [part.strip() for part in order_adress.split(",")]
        if len(parts) != 3:
            raise ValidationError(_("Будь ласка, введіть адресу у вказаному форматі"))
        for part in parts:
            if len(part) < 3 or not part.isalpha():
                raise ValidationError(_("Будь ласка, введіть коректну адресу"))
        return order_adress

    delivery_method = forms.ChoiceField(
        label=_("Спосіб доставки"),
        choices=[
            ('Почта России (Россия)', 'Почта России (Россия)'),
            ('СДЭК (Россия)', 'СДЭК (Россия)'),
            ('Сourier (Only for Moscow and Berlin)', 'Сourier (Only for Moscow and Berlin)'),
            ('DHL (Europe)', 'DHL (Europe)'),
            ('UPS (Europe)', 'UPS (Europe)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean_delivery_method(self):
        delivery_method = self.cleaned_data.get('delivery_method')
        if delivery_method not in ['Почта России (Россия)', 'СДЭК (Россия)', 'Сourier (Only for Moscow and Berlin)', 'DHL (Europe)', 'UPS (Europe)']: 
            raise ValidationError(_("Вибраний спосіб доставки некоректний"))
        return delivery_method


    payment_method = forms.ChoiceField(
        label=_("Спосіб оплати"),
        choices=[
            ('Cash on delivery', 'Cash on delivery'),
            ('On card', 'On card'),
            ('Crypto', 'Crypto'),
        ],
        widget=forms.TextInput(attrs={"type": "hidden"})
    )

    def clean_payment_method(self):
        payment_method = self.cleaned_data.get('payment_method')
        if payment_method not in ['Cash on delivery', 'On card', 'Crypto']: 
            raise ValidationError(_("Вибраний спосіб оплати некоректний"))
        return payment_method

    def get_recipient_name(self):
        parts = [self.cleaned_data.get("last_name"), self.cleaned_data.get("first_name"), self.cleaned_data.get("patronymic")]
        return " ".join(filter(None, parts))

    class Meta:
        model = Order
        fields = ['phone_number', 'first_name', 'last_name', 'patronymic', 'order_adress', 'delivery_method', 'payment_method']
        

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_("Новый пароль"), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Введите новый пароль')}))
    new_password2 = forms.CharField(label=_("Подтверждение пароля"), widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Подтвердите новый пароль')}))