from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, logout, login
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from django.urls import reverse_lazy
from .models import Product, Product_Category, Order, OrderItem, Message, ViewProd
from .utils import send_activation_email, Cart, Viewed
from django.contrib import messages
from SmartZamovApp import forms
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.auth.decorators import login_required
import re, os
from django.http import FileResponse
from django.utils import timezone
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.utils import translation

def get_accesoaries_products(request, product):
    target_brand = product.brand
    target_product_correct = None
    
    target_products = Product.objects.filter(brand=target_brand).exclude(id=product.id).order_by('price')
    first_product = target_products.first()

    if product.price_en > 100:
        if first_product and first_product.price_en <= 100 and first_product.category.name != product.category.name:
            target_product_correct = first_product
        
        if request.user.is_authenticated:
            user = request.user
            liked_product_ids = user.liked_products.values_list('id', flat=True)
            liked_products = target_products.filter(id__in=liked_product_ids).order_by('price')
            first_liked_product = liked_products.first()
            if first_liked_product and first_liked_product.price_en <= 100 and first_liked_product.category.name != product.category.name:
                target_product_correct = first_liked_product
    
        # if not target_product_correct:
        #     target_products = Product.objects.all().exclude(id=product.id).order_by('price')
        #     if target_products.first().price_en <= 100:
        #         target_product_correct = target_products.first()
            
    return target_product_correct

def get_all_products():
    return list(Product.objects.all())

def normalize_price(price, min_price, max_price):
    return (price - min_price) / (max_price - min_price) if max_price > min_price else 0

def get_product_vectors(all_products, main_product):
    if not all_products:
        return np.array([]), None, None, None
    
    min_price = min(p.price_en for p in all_products)
    max_price = max(p.price_en for p in all_products)
    
    all_texts = [p.name + " " + p.description for p in all_products]
    vectorizer = TfidfVectorizer(max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(all_texts).toarray()
    
    product_vectors = []
    for i, product in enumerate(all_products):
        text_vector = tfidf_matrix[i]
        normalized_price = normalize_price(product.price_en, min_price, max_price)
        
        tag_match = 1.0 if set(product.tags.values_list('id', flat=True)) & set(main_product.tags.values_list('id', flat=True)) else 0.0
        category_match = 1.0 if product.category.name == main_product.category.name else 0.0
        brand_match = 1.0 if product.brand == main_product.brand else 0.0
        
        weight_category = 0.7

        additional_features = np.array([normalized_price, weight_category * category_match, brand_match, tag_match])
        vector = np.concatenate((additional_features, text_vector))
        product_vectors.append(vector)
    
    return np.array(product_vectors), vectorizer, tfidf_matrix, (min_price, max_price)

def find_similar_products(product, top_n=5):
    all_products = get_all_products()
    if not all_products:
        return []
    
    product_vectors, vectorizer, tfidf_matrix, price_range = get_product_vectors(all_products, product)
    
    if product_vectors.size == 0:
        return []
    
    n_neighbors = min(top_n + 1, len(all_products))
    knn = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
    knn.fit(product_vectors)
    
    product_index = next((i for i, p in enumerate(all_products) if p.id == product.id), None)
    if product_index is None:
        return []
    
    distances, indices = knn.kneighbors([product_vectors[product_index]], n_neighbors=n_neighbors)
    similar_products = [all_products[i] for i in indices[0] if all_products[i].id != product.id]
    
    return similar_products[:top_n]

def RefreshViewedProdList(viewed_products, user):
    for product_data in viewed_products.default_iter():
        created_time = datetime.fromisoformat(product_data['add_time'])
        
        if created_time.tzinfo is None:
            created_time = timezone.make_aware(created_time)

        viewed_product, created = ViewProd.objects.get_or_create(user=user, product=product_data['item'])        
        if viewed_product.created != created_time:
            viewed_product.created = created_time
        viewed_product.save()

    viewed_products.clear()

def product_viewed(request, product):
    if request.user.is_authenticated:
        viewed_prod, created = ViewProd.objects.get_or_create(user=request.user, product=product)
        if not created:
            viewed_prod.created = timezone.now()
            viewed_prod.save()
    else:
        viewed_prod = Viewed(request)
        viewed_prod.add_product(product)

def get_unread(request):
    if request.user.is_authenticated:
        return request.user.count_unread_messages()
    else: 
        return None

def get_cart(request):
    if request.user.is_authenticated:
        return request.user.orders.filter(status="On cart", is_paid=False).first()
    else:
        return Cart(request)
    
def get_viewed_products(request):
    if request.user.is_authenticated:
        return ViewProd.objects.filter(user=request.user).order_by('-created')
    else:
        return Viewed(request)

def download_pdf(request):
    pdf_path = os.path.join('static', 'documents', 'Условия конфиденциальности.pdf')
    return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')

class PasswordChange(PasswordChangeView):
    template_name="profile_change_password.html"
    form_class=forms.ChangePasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = get_cart(self.request)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        return response
    
class PasswordReset(PasswordResetView):
    template_name="forgot_password.html"
    form_class=forms.ResetPasswordForm
    success_url = reverse_lazy("password_reset_done") 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = get_cart(self.request)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        return response
    

class SignInView(LoginView):
    template_name = 'sign_in.html'
    authentication_form = forms.UserLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = get_cart(self.request)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        session_cart = Cart(self.request)
        viewed_products = Viewed(self.request)

        if user.is_authenticated:
            if viewed_products.count() > 0:
                RefreshViewedProdList(viewed_products, user)

            if session_cart.count() > 0:
                order, created = Order.objects.get_or_create(user=user, status='On cart', is_paid=False)
                
                for item in session_cart:
                    orderitem, orderitem_created = OrderItem.objects.get_or_create(
                        order=order,
                        product=item['product'],
                        defaults={'quantity': item['quantity']}
                    )
                    if not orderitem_created:
                        orderitem.quantity = item['quantity']
                        orderitem.save()
                
                order.save()

                session_cart.clear()

        return response

def WishList(request):
    cart = get_cart(request)
    unread_messages = get_unread(request)
    if not request.user.is_authenticated:
        return redirect("index")
    target_order = None
    if request.method == "GET":
        order_id = request.GET.get('order_id', None)
        if order_id:
            target_order = request.user.orders.filter(id=order_id).first()
    liked_products = request.user.liked_products.all
    orders = request.user.orders.all()
    last_orders = orders.order_by('-created')[:3]
    return render(request, 'profile_page_wishlist.html', {'liked_products': liked_products, "cart": cart, "orders": last_orders, "target_order": target_order, "unread_messages": unread_messages})

def ToogleToFavorite(request):
    if request.user.is_authenticated:
        if request.POST:
            form = forms.FavoriteProductsForm(request.POST)
            if form.is_valid():
                selected_products = form.cleaned_data['product_ids']
                for product in selected_products:
                    try: 
                        product_viewed(request, product)
                        if product in request.user.liked_products.all():
                            request.user.liked_products.remove(product)
                        else:
                            request.user.liked_products.add(product)
                    except Product.DoesNotExist:
                        messages.error(request, _('Товар не знайдено'))
    else:
        messages.error(request, _('Спочатку увійдіть до свого акаунту!'))
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def LogoutUser(request):
    if request.user.is_authenticated:
        User_order = request.user.orders.filter(status="On cart", is_paid=False).first()
        viewed_prod_obj = get_viewed_products(request)
        logout(request)
        if User_order:            
            session_cart = Cart(request)
            for item in User_order.items.all():                
                session_cart.add(product=item.product, quantity=item.quantity)
            User_order.delete()
        if viewed_prod_obj.count() > 0:            
            for item in viewed_prod_obj:                
                new_viewed_prod = Viewed(request)
                new_viewed_prod.add_product(product=item.product, time=item.created)
        messages.success(request, _('Ви успішно вийшли зі свого профілю'))
    return redirect('index')

def ProductView(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        cart = get_cart(request)
        unread_messages = get_unread(request)
        similar_products = find_similar_products(product)
        also_you_may_need_product = get_accesoaries_products(request, product)
        product_viewed(request, product)
        return render(request, 'product_page.html', {'product': product, "cart": cart, "unread_messages": unread_messages, "similar_products": similar_products, "also_you_may_need_product": also_you_may_need_product})
    except Product.DoesNotExist:
        messages.error(request, _('Товар не знайдено'))
        return redirect(request.META.get('HTTP_REFERER', 'index'))

def PersonalAccount(request):
    if not request.user.is_authenticated:
       return redirect('index')
    cart = get_cart(request)
    unread_messages = get_unread(request)
    target_order = None
    orders = request.user.orders.all()
    last_orders = orders.order_by('-created')[:3]
    if request.method=="POST":
        form = forms.ChangeUserData(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данні в вашому профілі успішно змінено')
            return redirect("personal_account")
    else:
        if request.method == "GET":
            order_id = request.GET.get('order_id', None)
            if order_id:
                target_order = request.user.orders.filter(id=order_id).first()
        user = request.user
        initial_data = {'phone_number': user.phone_number, 'username': user.username, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name, 'adress': user.adress, "patronymic": user.patronymic}
        form = forms.ChangeUserData(initial=initial_data)
    return render(request, 'user_profile.html', {'form': form, "cart": cart, "orders": last_orders, "target_order": target_order, "unread_messages": unread_messages})

def SignUp(request):
    if request.user.is_authenticated:
        return redirect('index')
    cart = get_cart(request)
    unread_messages = get_unread(request)
    if request.method=='POST':
        form = forms.UserRegistrationForm(request.POST)
        if form.is_valid():
            form.clean_email()
            form.clean_phone()
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            viewed_prod = get_viewed_products(request)

            if viewed_prod.count() > 0:
                RefreshViewedProdList(viewed_prod, user)

            user.save()
            order = Order.objects.create(user=user, status="On cart", is_paid=False)
            for item in cart:
                order_item = OrderItem.objects.create(order=order, product=item['product'], quantity=item['quantity'])
                order_item.save()
            order.save()
            send_activation_email(user, request)
            messages.success(request, _('Письмо с подтверждением отправлено на вашу электронную почту.'))
            return redirect('sign_in')
    else:
        form = forms.UserRegistrationForm()
    return render(request, 'sign_up.html', {'form': form, "cart": cart, "unread_messages": unread_messages})

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, _("Ваш аккаунт успешно активированый!"))
        return redirect('sign_in')
    else:
        messages.error(request, _("Ссылка активации недействительна или устарела!"))
        return redirect('index')

def index(request):
    viewed_products = get_viewed_products(request)
    unread_messages = get_unread(request)
    cart = get_cart(request)
    All_products_categories = Product_Category.objects.all()
    products = Product.objects.all()
    new_products = products.order_by('-created')[:5]
    all_brands = sorted(set(Product.objects.values_list('brand', flat=True)))
    is_search = False
    for product in new_products:
        product.description = re.sub(r'<.*?>', '', product.description)

    if request.method == "GET":
        category = request.GET.get('category', None)
        available = request.GET.get('available', None) 
        sort_by = request.GET.get('sort_by', 'name')
        order = request.GET.get('order', 'asc')
        requestToSearch = request.GET.get('requestToSearch', None)
        selected_brands = list(set(request.GET.getlist('brand')))
        selected_tags = list(set(request.GET.getlist('tag')))

        if requestToSearch:
            new_products = None
            is_search = True
            products = products.filter(name__icontains=requestToSearch) | products.filter(description__icontains=requestToSearch)

        if category:
            new_products = None
            is_search = True
            products = products.filter(category__slug=category)

        if available:
            new_products = None
            is_search = True
            products = products.filter(available=available) 

        if sort_by in ['name', 'price', 'created']:
            if order == 'desc':
                sort_by = f'-{sort_by}'
            products = products.order_by(sort_by)
        
        if selected_brands:
            new_products = None
            is_search = True
            products = products.filter(brand__in=selected_brands)
            
        if selected_tags:
            new_products = None
            is_search = True
            products = products.filter(tags__name__in=selected_tags)

    return render(request, 'index.html', {'products': products, 'All_products_categories': All_products_categories, 'new_products': new_products, "cart": cart, "unread_messages": unread_messages, "viewed_products": viewed_products, 'is_search': is_search, 'all_brands': all_brands, 'selected_brands': selected_brands, 'selected_tags': selected_tags})

def ViewAboutUsPage(request):
    cart = get_cart(request)
    unread_messages = get_unread(request)
    return render(request, 'about_us.html', {"cart": cart, "unread_messages": unread_messages})

@login_required
def ViewOrders(request):
    cart = get_cart(request)
    unread_messages = get_unread(request)
    if not request.user.is_authenticated:
        return redirect("index")
    target_order = None
    if request.method == "GET":
        order_id = request.GET.get('order_id', None)
        if order_id:
            target_order = request.user.orders.filter(id=order_id).first()
    All_orders = request.user.orders.all().order_by('-created')
    return render(request, 'user_profile_orders.html', {"cart": cart, "orders": All_orders, "target_order": target_order, "unread_messages": unread_messages})

def PaswordSuccessfullyChanged(request):
    messages.success(request, _('Пароль успішно змінено!'))
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def PasswordResetDone(request):
    messages.success(request, _('Ми відправили вам інструкції для скидання пароля на вказану вами електронну адресу.'))
    return redirect('index')

def CartAdd(request, slug):
    try:
        Target_product = Product.objects.get(slug=slug)
        product_viewed(request, Target_product)
        if request.user.is_authenticated:
            order, created = Order.objects.get_or_create(user=request.user, status='On cart', is_paid=False)
            orderitem, orderitem_created = OrderItem.objects.get_or_create(order=order, product=Target_product, defaults={'quantity': 1})
            if not orderitem_created:
                orderitem.quantity += 1
                orderitem.save()
            order.save()
        else:
            cart = Cart(request)
            cart.add(Target_product, quantity=1)
    except Product.DoesNotExist:
        messages.error(request, _('Товар не знайдено'))
    url = request.META.get('HTTP_REFERER', f'/product-detail/{slug}/')
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params['cartopen'] = ['true']
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))
    return redirect(new_url)

def CartRemove(request, slug):
    RemoveAll = request.GET.get('RemoveAll', False)
    try:
        cart = get_cart(request)
        Target_product = Product.objects.get(slug=slug)
        
        if request.user.is_authenticated:
            item = cart.items.get(product=Target_product)
            item.delete()
            cart.save()
        else:
            cart.remove(Target_product, remove_all=RemoveAll)
    except Product.DoesNotExist:
        messages.error(request, _('Товар не знайдено'))

    url = request.META.get('HTTP_REFERER', f'/product-detail/{slug}/')
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params['cartopen'] = ['true']
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))
    return redirect(new_url)

def CartUpdate(request, slug):
    try:
        if request.method=='POST':
            Target_product = Product.objects.get(slug=slug)
            cart = get_cart(request)
            quantity_change_method = request.POST.get('action', None)
            if request.user.is_authenticated:
                Target_order_item = cart.items.get(product=Target_product)
                if quantity_change_method == "increase":
                    Target_order_item.quantity += 1
                elif quantity_change_method == "decrease":
                    Target_order_item.quantity -= 1
                if Target_order_item.quantity > 0:
                    Target_order_item.save()
                elif Target_order_item.quantity == 0:
                    Target_order_item.delete()
                cart.save()
            else:
                if quantity_change_method == "increase":
                    cart.remove(product=Target_product, quantity=-1, remove_all=False)
                elif quantity_change_method == "decrease":
                    cart.remove(product=Target_product, quantity=1, remove_all=False)            
    except Product.DoesNotExist:
        messages.error(request, _('Товар не знайдено'))
    url = request.META.get('HTTP_REFERER', f'/product-detail/{slug}/')
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params['cartopen'] = ['true']
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))
    return redirect(new_url)

def Checkout(request):
    if not request.user.is_authenticated:
        messages.error(request, _('Спочатку увійдіть до свого акаунту!'))
        return redirect(request.META.get('HTTP_REFERER', 'index'))

    cart = get_cart(request)
    if cart.total < 1:
        messages.error(request, _('В кошику ще нічого немає!'))
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    unread_messages = get_unread(request)

    count_cart_items = sum(item.quantity for item in cart.items.all())

    if request.method == "POST":
        form = forms.PlaceOrder(request.POST, instance=cart) 
        if form.is_valid():
            order = form.save(commit=False)

            user = request.user
            if not user.adress:
                user.adress = form.cleaned_data['order_adress']
            if not user.phone_number:
                user.phone_number = form.cleaned_data['phone_number']
            if not user.patronymic:
                user.patronymic = form.cleaned_data['patronymic']
            if not user.first_name:
                user.first_name = form.cleaned_data['first_name']
            if not user.last_name:
                user.last_name = form.cleaned_data['last_name']
            user.save()
            
            order.status = "Waiting_for_payment"
            lang = translation.get_language()
            if lang.startswith('ru'):
                if order.delivery_method == "Сourier (Only for Moscow and Berlin)":
                    if order.payment_method=="Cash on delivery":
                        order.due_for_payment_now=1499
                        order.due_for_payment_now_ru=1499
                    else:
                        order.due_for_payment_now=order.total+1499
                        order.due_for_payment_now_ru=order.total+1499
                else:
                    if order.payment_method=="Cash on delivery":
                        order.due_for_payment_now=799
                        order.due_for_payment_now_ru=799
                    else:
                        order.due_for_payment_now=order.total+799
                        order.due_for_payment_now_ru=order.total+799
            elif lang.startswith('en'):
                if order.delivery_method == "Сourier (Only for Moscow and Berlin)":
                    if order.payment_method=="Cash on delivery":
                        order.due_for_payment_now=14.99
                        order.due_for_payment_now_en=14.99
                    else:
                        order.due_for_payment_now=order.total+14.99
                        order.due_for_payment_now_en=order.total+14.99
                else:
                    if order.payment_method=="Cash on delivery":
                        order.due_for_payment_now=9.99
                        order.due_for_payment_now_en=9.99
                    else:
                        order.due_for_payment_now=order.total+9.99
                        order.due_for_payment_now_en=order.total+9.99
            elif lang.startswith('de'):
                if order.delivery_method == "Сourier (Only for Moscow and Berlin)":
                    if order.payment_method=="Cash on delivery":
                        order.due_for_payment_now=14.99
                        order.due_for_payment_now_de=14.99
                    else:
                        order.due_for_payment_now=order.total+14.99
                        order.due_for_payment_now_de=order.total+14.99
                else:
                    if order.payment_method=="Cash on delivery":
                        order.due_for_payment_now=9.99
                        order.due_for_payment_now_de=9.99
                    else:
                        order.due_for_payment_now=order.total+9.99
                        order.due_for_payment_now_de=order.total+9.99
                    
            order.recipient_name = form.get_recipient_name()
            order.save()

            return redirect('PayForOrder', id=order.id)
        else:
            messages.error(request, _('Введені дані є некоректними або не заповнені!'))
    else:
        initial_data = {'phone_number': request.user.phone_number, 'username': request.user.username, 'email': request.user.email, 'first_name': request.user.first_name, 'last_name': request.user.last_name, 'patronymic': request.user.patronymic, 'order_adress': request.user.adress, 'delivery_method': cart.delivery_method}
        form = forms.PlaceOrder(initial=initial_data)

    return render(request, 'checkout_page.html', {"cart": cart, "count_cart_items": count_cart_items, "form": form, "unread_messages": unread_messages})

def PayForOrder(request, id):
    if not request.user.is_authenticated:
        messages.error(request, _('Спочатку увійдіть до свого акаунту!'))
        return redirect(request.META.get('HTTP_REFERER', 'index'))
        
    target_order = Order.objects.get(id=id)
    
    if target_order.is_paid == True:
        return redirect('PaymentSucess')
    
    cart = get_cart(request)
    unread_messages = get_unread(request)

    success = False
    
    if request.method == "GET":
        if success:
            message_text = 'Your order has been successfully received! We will prepare it for shipment shortly. Thank you for your purchase! 🚀'
            message = Message.objects.create(user=request.user, order=cart, text=message_text)
            message.text_en = "Your order has been successfully received! We will prepare it for shipment shortly. Thank you for your purchase! 🚀"
            message.text_ru = "Ваш заказ успешно принят! В ближайшее время мы подготовим его к отправке. Спасибо за покупку! 🚀"
            message.text_de = "Ihre Bestellung wurde erfolgreich angenommen! Wir bereiten sie in Kürze für den Versand vor. Vielen Dank für Ihren Einkauf! 🚀"
            message.save()
            return redirect('orders')

    return render(request, 'payment_for_the_order.html', {"cart": cart, "unread_messages": unread_messages, "target_order": target_order})

def ViewMessages(request):
    if not request.user.is_authenticated:
        return redirect("index")
    unread_messages = get_unread(request)
    target_order = None
    if request.method == "GET":
        order_id = request.GET.get('order_id', None)
        if order_id:
            target_order = request.user.orders.filter(id=order_id).first()
    cart = get_cart(request)
    all_messages = request.user.messages.all().order_by('-created')
    all_messages.filter(is_read=False).update(is_read=True) 
    return render(request, 'user_profile_messages.html', {"cart": cart, 'all_messages': all_messages, 'target_order': target_order, "unread_messages": 0})

def PaymentSucess(request):
    unread_messages = get_unread(request)
    cart = get_cart(request)
    return render(request, 'payment_success.html', {"cart": cart, "unread_messages": unread_messages})

def PaymentFailed(request):
    unread_messages = get_unread(request)
    cart = get_cart(request)
    return render(request, 'payment_failed.html', {"cart": cart, "unread_messages": unread_messages})

def payment_notification(request):
    return redirect('index')
    
def PasswordResetSuccess(request):
    messages.success(request, _('Пароль успішно змінено! Тепер ви можете увійти до свого акаунту, використовуючи його.'))
    return redirect('index')

def error_404(request, exception):
    unread_messages = get_unread(request)
    cart = get_cart(request)
    return render(request, '404.html', {'cart': cart, 'unread_messages': unread_messages}, status=404)

from django.shortcuts import render

def error_500(request):
    unread_messages = get_unread(request)
    cart = get_cart(request)
    return render(request, '500.html', {'cart': cart, 'unread_messages': unread_messages}, status=500)
    