from django.urls import path
from .views import (
    checkout,
    ItemDetailView,
    HomeView,
    add_to_cart,
    remove_from_cart
)

app_name = 'core'


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>/',ItemDetailView.as_view() , name='product'),
    path('checkout/', checkout, name='checkout'),
    path('add_to_cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),

]