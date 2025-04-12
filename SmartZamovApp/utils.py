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
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, tempfile, os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def clear_cart(driver):
    elements_all_div = driver.find_elements(By.XPATH, '/html/body/div[11]/div/div[2]/div[2]/div[1]')
    if len(elements_all_div) == 0:
        close_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[11]/div/div[2]/svg')))
        close_btn.click()
        return
    
    elements_all_div[0].find_element(By.XPATH, './/div[@role="button" and @aria-label="Add item to cart"]').click()
    time.sleep(0.1)
    if len(elements_all_div) > 1:
        clear_cart(driver)
    else:
        return
    
def buy_skin_with_bot(recomended_price, card_number, card_expiry, card_cvv, card_owner_initials):
    driver = None
    
    try:
        card_expiry = card_expiry.replace('/', '')
        card_expiry = card_expiry.replace(' ', '')
        card_expiry = card_expiry[:2] + "20" + card_expiry[2:]
    
        options = webdriver.ChromeOptions()
        options.binary_location = "/usr/bin/chromium-browser"
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--lang=ru-RU')
        options.add_argument('--disable-extensions')
        options.add_argument('--incognito')

        driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=options)
    
        driver.get('https://cs.money/ru/market/buy/')
    
        time.sleep(1)
    
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[//span[text()="Принять все"]]'))
            )
            button.click()
        except:
            pass
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_cookie_path = os.path.join(BASE_DIR, 'cookies.json')
        file_local_storage_path = os.path.join(BASE_DIR, 'local_storage.json')
        file_session_storage_path = os.path.join(BASE_DIR, 'session_storage.json')
    
        with open(file_cookie_path, 'r') as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            driver.add_cookie(cookie)
    
        with open(file_local_storage_path, "r") as file:
            local_storage = json.load(file)
    
        for local_storage_item in local_storage:
            driver.execute_script(f"window.localStorage.setItem('{local_storage_item}', '{local_storage[local_storage_item]}')")
    
        with open(file_session_storage_path, "r") as file:
            session_storage = json.load(file)
    
        for session_storage_item in session_storage:
            driver.execute_script(f"window.sessionStorage.setItem('{session_storage_item}', '{session_storage[session_storage_item]}')")
            
        time.sleep(1)
    
        driver.refresh()
    
        time.sleep(3)
        
        driver.save_screenshot("/www/wwwroot/msk52.shop/screenshot.png")
    
        try:
            close_btn = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[10]/div/div[2]/svg')))
            close_btn.click()
        except:
            pass
    
        buy_cart = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/astro-island/div/div[1]/div[4]/div/astro-slot/div/div/astro-island[1]/div/div/div[2]/div[1]/div[2]/button'))
        )    
        buy_cart.click() #Открыть корзину
    
        time.sleep(1)
    
        clear_cart(driver)
    
        time.sleep(1)
    
        instant_buy_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="layout-page-content-area"]/div/astro-slot/div/div/astro-island[1]/div/div/div[1]/div/div[2]/div[3]/div[2]/div[1]/label')))
        instant_buy_button.click() #Мгновенная покупка кликнуть
    
        time.sleep(1)
    
        driver.find_element(By.XPATH, '//*[@id="support-widget-parent"]/div[1]/div[1]/button').click() #Выбор сортировки по цене
    
        time.sleep(1)
        
        driver.find_element(By.XPATH, '//div[div[2][div[text()="Цена: Макс."]]]').click() #Выбор опции сортировки по цене
        driver.find_element(By.XPATH, '//*[@id="layout-page-header"]/astro-slot/astro-island/div/div/div[2]/div[3]').click() #Выбор валюты
    
        time.sleep(1)
    
        driver.find_element(By.XPATH, '//div[div[div[text()="₽ RUB"]]]').click() #Выбор валюты РУБЛЯ
    
        time.sleep(1)
    
        driver.find_element(By.XPATH, '//*[@id="layout-page-content-area"]/div/astro-slot/div/div/astro-island[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div/div[3]/div/div/div/input').send_keys(recomended_price) #Ввести цену
    
        time.sleep(1)
    
        target_skin = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/astro-island/div/div[1]/div[4]/div/astro-slot/div/div/astro-island[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div//div[@role="button" and @aria-label="Add item to cart"]'))
        )
        try:
            target_skin.find_element(By.XPATH, './div[@class="csm_a27c0aec csm_cddc87c8 csm_21681837"]')
        except:
            target_skin.click() # Добавить товар в корзину
    
        time.sleep(1)
    
        buy_cart = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/astro-island/div/div[1]/div[4]/div/astro-slot/div/div/astro-island[1]/div/div/div[2]/div[1]/div[2]/button')) # Оформить заказ
        )    
        buy_cart.click() #Открыть корзину
    
        time.sleep(2.5)
    
        driver.find_element(By.XPATH, '/html/body/div[11]/div/div[2]/div[2]/div[3]/button').click()
    
        but_pay = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,  '/html/body/div[15]/div/div/div/div[4]/div/div/div/div/div/div/div[2]/div/div[4]/button'))
        )
        but_pay.click() #Заплатить сумму
    
        time.sleep(1)
    
        driver.switch_to.window(driver.window_handles[-1])
    
        time.sleep(1)
    
        driver.find_element(By.XPATH, '//*[@id="input-card-number"]').send_keys(card_number)
        driver.find_element(By.XPATH, '//*[@id="card-expires"]').send_keys(card_expiry)
        driver.find_element(By.XPATH, '//*[@id="input-card-cvc"]').send_keys(card_cvv)
        driver.find_element(By.XPATH, '//*[@id="input-card-holder"]').send_keys(card_owner_initials)
    
        time.sleep(1)
    
        driver.find_element(By.XPATH, '//*[@id="action-submit"]').click()
    
        time.sleep(7)
    
        target_url = driver.current_url
    
        driver.quit()
    
        return target_url
        
    finally:
        if driver:
            driver.quit()
    
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