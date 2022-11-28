from django.urls import path
from .views import *


urlpatterns = [
    path('', all_products, name="products"),
    path('product/<int:pk>', card_product, name="page_product"),
    path('order/', order, name="order"),
    path('order_add/<int:pk>', order_add, name="order_add"),
    path('order_remove/<int:pk>', order_remove, name="order_remove"),
    path('order_info/', order_info, name="order_info"),
    path('create_checkout_session/<int:pk>', create_checkout_session, name="create_checkout_session"),
    path('order/create_checkout_session_oders', create_checkout_session_oders, name="create_checkout_session_orders"),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('cancel/', cancel, name='cancel'),
    path('success/<slug:pk>', success, name='success'),
]
