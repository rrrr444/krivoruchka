from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.shortcuts import redirect

def custom_logout(request):
    messages.success(request, "Вы успешно вышли из системы")
    return LogoutView.as_view(next_page='home')(request)

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('add-product/', views.add_product, name='add_product'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:cart_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('logout/', custom_logout, name='logout'),
    path('order-history/', views.order_history, name='order_history'),
    path('orders/confirm/<int:order_id>/', views.confirm_receipt, name='confirm_receipt'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),
    path('seller/orders/<int:order_id>/ship/', views.mark_order_shipped, name='mark_order_shipped'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('confirm/ship/<int:order_id>/', views.confirm_shipment, name='confirm_shipment'),
    path('confirm/deliver/<int:order_id>/', views.confirm_delivery, name='confirm_delivery'),
    path('buyer/orders/', views.buyer_orders, name='buyer_orders'),
    path('sales/', views.sales_list, name='sales_list'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('confirm/ship/<int:order_id>/', views.confirm_shipment, name='confirm_shipment'),
    path('seller/orders/', views.seller_orders, name='seller_orders'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)