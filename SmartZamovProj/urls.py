"""
URL configuration for SmartZamovProj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from SmartZamovApp import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import set_language
from django.urls import reverse_lazy
from SmartZamovApp.forms import CustomSetPasswordForm

handler404 = views.error_404
handler500 = views.error_500

urlpatterns = [
    path('terms/', views.download_pdf, name='download_pdf'),
    path('', views.index, name='index'),
    path('products-detail/add-to-favotite', views.ToogleToFavorite ,name="Toogle_to_favorite"),
    path('admin/', admin.site.urls),
    path('set_language/', set_language, name='set_language'),
    path('sign-up/', views.SignUp, name='sign_up'),
    path('sign-in/', views.SignInView.as_view(), name='sign_in'),
    path('forgot-password/', views.PasswordReset.as_view(), name='forgot_password'),
    path('accounts/<uidb64>/<token>/activate/', views.activate_account, name='activate_account'),
    path('accounts/profile/', views.PersonalAccount ,name="personal_account"),
    path('accounts/logout/', views.LogoutUser ,name="logout"),
    path('product-detail/<slug:slug>/', views.ProductView, name="ViewProduct"),
    path('product-detail/<slug:slug>/add-to-cart/', views.CartAdd, name="AddToCartProduct"),
    path('product-detail/<slug:slug>/remove-from-cart/', views.CartRemove, name="RemoveFromCartProduct"),
    path('product-detail/<slug:slug>/update-count-of-product-cart/', views.CartUpdate, name="CartUpdate"),
    path('checkout/', views.Checkout, name="checkout"),
    path('checkout/order-pay/<int:id>/', views.PayForOrder, name="PayForOrder"),
    path('checkout/payment-success/', views.PaymentSucess, name="PaymentSucess"),
    path('checkout/payment-failed/', views.PaymentFailed, name="PaymentFailed"),
    path('payment-notification/', views.payment_notification, name='payment_notification'),
    path('accounts/profile/wishlist/', views.WishList ,name="wishlist"),
    path('accounts/profile/orders/', views.ViewOrders, name='orders'),
    path('about_us/', views.ViewAboutUsPage, name="about_us"),
    path('accounts/profile/change-password/', views.PasswordChange.as_view() , name="ChangePassword"),
    path('accounts/profile/change-password/done/', views.PaswordSuccessfullyChanged, name="password_change_done"),
    path('forgot-password/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(form_class = CustomSetPasswordForm, template_name="password_reset_confirm.html", success_url = reverse_lazy('password_reset_success')), name='password_reset_confirm'),
    path('forgot-password/password_reset_done/', views.PasswordResetDone, name="password_reset_done"),
    path('forgot-password/password_changed_successfully/', views.PasswordResetSuccess, name="password_reset_success"),
    path('accounts/profile/messages/', views.ViewMessages, name='view_messages'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)