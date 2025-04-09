from django import forms
from .models import CustomUser, Product, Product_Category, Order, BankCards
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.backends import BaseBackend
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import datetime

class FavoriteProductsForm(forms.Form):
    product_ids = forms.ModelMultipleChoiceField(queryset=Product.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

class ChangeUserData(forms.ModelForm):
    username = forms.CharField(label=_("Нікнейм: "), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Введіть імя користувача')}))    
    email = forms.EmailField(label=_("Електронна пошта: "), required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Введіть електронну пошту')}))    
    first_name = forms.CharField(label=_("Ім'я користувача: "), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Введіть ваше ім'я")}))    
    last_name = forms.CharField(label=_("Фамілія користувача: "), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':  _("Введіть вашу фамілію")}))    
    patronymic = forms.CharField(label=_("По батькові: "), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':  _("По батькові")}))    
    phone_number = forms.CharField(label=_("Номер телефону: "), required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Введіть ваш номер телефону")}))    
    adress = forms.CharField(label=_("Адрес (Область, город, слово 'улица' + название улицы + номер дома): "),required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Московская область, Москва, улица Тверская 10.")}))

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
            raise ValidationError(_("Формат адреса неверный. Пожалуйста, введите адрес в следующем формате: (Область, город, слово 'улица' + название улицы + номер дома). Плюсики и другие символы не используются. Пример: Московская область, Москва, улица Тверская 10."))
    
        for i, part in enumerate(parts):
            if i == 0:
                if len(part) < 3 or not part.isalpha():
                    raise ValidationError(_("Название области должно содержать только буквы и быть длиннее двух символов."))
            elif i == 1:
                if len(part) < 3 or not part.isalpha():
                    raise ValidationError(_("Название города должно содержать только буквы и быть длиннее двух символов."))
            elif i == 2:
                if not any(word in part.lower() for word in ['улица', 'street', 'Straße']):
                    raise ValidationError(_("Необходимо указать слово 'улица' в названии улицы."))
                parts_of_address = part.lower().split("улица")
                if len(parts_of_address) != 2 or not parts_of_address[1].strip():
                    raise ValidationError(_("После слова 'улица' должно следовать название улицы и номер дома."))
                try:
                    street, house = parts_of_address[1].strip().split(" ", 1)
                    if not house.isdigit():
                        raise ValidationError(_("Номер дома должен быть числом."))
                except:
                    raise ValidationError(_("После слова 'улица' должно следовать название улицы и номер дома."))
                    raise ValidationError(_("Номер дома должен быть числом."))
    
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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 999-99-99'}),
        required=False
    )

    first_name = forms.CharField(
        label=_("Ім'я отримувача"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Іван')}),
        required=False
    )

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError(_("Пожалуйста, заполните это поле. Оно является обязательным."))
        if not first_name.isalpha():
            raise ValidationError(_("Ім'я повинно містити лише літери"))
        if len(first_name) < 2:
            raise ValidationError(_("Ім'я повинно бути не менше 2 символів"))
        return first_name

    last_name = forms.CharField(
        label=_("Прізвище отримувача"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Іванов')}),
        required=False
    )

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError(_("Пожалуйста, заполните это поле. Оно является обязательным."))
        if not last_name.isalpha():
            raise ValidationError(_("Прізвище повинно містити лише літери"))
        if len(last_name) < 2:
            raise ValidationError(_("Прізвище повинно бути не менше 2 символів"))
        return last_name

    patronymic = forms.CharField(
        label=_("По батькові отримувача"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Іванович')}),
        required=False
    )

    def clean_patronymic(self):
        patronymic = self.cleaned_data.get('patronymic')
        if not patronymic:
            raise ValidationError(_("Пожалуйста, заполните это поле. Оно является обязательным."))
        if not patronymic.isalpha():
            raise ValidationError(_("По батькові повинно містити лише літери"))
        return patronymic

    order_adress = forms.CharField(
        label=_("Адрес (Область, город, слово 'улица' + название улицы + номер дома): "),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Московская область, Москва, улица Тверская 10.')}),
        required=False
    )

    def clean_order_adress(self):
        order_adress = self.cleaned_data['order_adress']
        if not order_adress:
            raise ValidationError(_("Пожалуйста, заполните это поле. Оно является обязательным."))
    
        parts = [part.strip() for part in order_adress.split(",")]
        
        if len(parts) != 3:
            raise ValidationError(_("Формат адреса неверный. Пожалуйста, введите адрес в следующем формате: (Область, город, слово 'улица' + название улицы + номер дома). Плюсики и другие символы не используются. Пример: Московская область, Москва, улица Тверская 10."))
    
        for i, part in enumerate(parts):
            if i == 0:
                if len(part) < 3 or not part.isalpha():
                    raise ValidationError(_("Название области должно содержать только буквы и быть длиннее двух символов."))
            elif i == 1:
                if len(part) < 3 or not part.isalpha():
                    raise ValidationError(_("Название города должно содержать только буквы и быть длиннее двух символов."))
            elif i == 2:
                if not any(word in part.lower() for word in ['улица', 'street', 'Straße']):
                    raise ValidationError(_("Необходимо указать слово 'улица' в названии улицы."))
                parts_of_address = part.lower().split("улица")
                if len(parts_of_address) != 2 or not parts_of_address[1].strip():
                    raise ValidationError(_("После слова 'улица' должно следовать название улицы и номер дома."))
                try:
                    street, house = parts_of_address[1].strip().split(" ", 1)
                    if not house.isdigit():
                        raise ValidationError(_("Номер дома должен быть числом."))
                except:
                    raise ValidationError(_("После слова 'улица' должно следовать название улицы и номер дома."))
                    raise ValidationError(_("Номер дома должен быть числом."))
    
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
        if payment_method not in ['Cash on delivery', 'On card']: 
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
    
class PaymentForm(forms.ModelForm):
    card_number = forms.CharField(label=_('Номер карты'), widget=forms.TextInput(attrs={'type': 'text', 'id': 'CardNumber', 'class': 'card-number-input', 'inputmode': 'numeric', 'maxlength': '19', 'placeholder': '0000 0000 0000 0000'}), required=True)
    card_expiry = forms.CharField(label=_('ММ / ГГ'), widget=forms.TextInput(attrs={'type': 'text', 'id': 'cardDate', 'class': 'card-expiry-input', 'inputmode': 'numeric', 'maxlength': '7', 'placeholder': '00 / 00'}), required=True)
    card_cvv = forms.CharField(label='CVV', widget=forms.PasswordInput(attrs={'class': 'card-cvv-input', 'placeholder': '000', 'inputmode': 'numeric', 'pattern': '\d*', 'maxlength': '3', 'id': 'cardCvv'}), required=True)
    
    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')
        card_number = card_number.replace(' ', '').replace('-', '')
        
        if not card_number.isdigit():
            raise ValidationError(_('Введите корректный номер карты'))
        elif len(card_number) != 16:
            raise ValidationError(_('Введите корректный номер карты'))
        else:
            total_sum = 0
            reverse_digits = card_number[::-1]
            
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n -= 9
                
                total_sum += n
            
            if total_sum % 10 != 0:
                raise ValidationError(_('Введите корректный номер карты'))
                
        return card_number
        
    def clean_card_expiry(self):
        card_expiry = self.cleaned_data.get('card_expiry')
        
        month = int(card_expiry[:2])
        current_year = datetime.datetime.now().year
        card_year = int(card_expiry[5:])
        
        if month < 1 or month > 12:
            raise ValidationError(_('Введите корректную дату'))
        elif card_year < current_year % 100 or card_year > (current_year % 100) + 10:
            raise ValidationError(_('Введите корректную дату'))
        return card_expiry
    
    def clean_card_cvv(self):
        card_cvv = self.cleaned_data.get('card_cvv')
        if not card_cvv.isdigit():
            raise ValidationError(_('Введите корректный CVV'))
        elif len(card_cvv) != 3:
            raise ValidationError(_('Введите корректный CVV'))
        return card_cvv
    
    class Meta:
        model = BankCards
        fields = ['card_number', 'card_expiry', 'card_cvv']