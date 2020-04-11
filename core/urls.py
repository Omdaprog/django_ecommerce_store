from django.urls import path
from .views import (
    CheckoutView,
    ItemDetailView,
    HomeView,
    add_to_cart,
    remove_from_cart,
    OrderSummaryView,
    remove_item_from_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView,
)

app_name = 'core'


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>/',ItemDetailView.as_view() , name='product'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add_to_cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add_to_coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove_item_from_cart/<slug>/', remove_item_from_cart, name='remove_item_from_cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),

]