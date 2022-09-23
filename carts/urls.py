from django.urls import path

from greatkart import views
from .import views

urlpatterns = [
    path('',views.cart,name='cart'),
    path('add_cart/<int:product_id>/',views.add_cart,name='add_cart'),
    path('remove_cart/<int:babi>/<int:bunyi>/',views.remove_cart,name='remove_cart'),
    path('remove_cart_item/<int:lanli>/<int:london>/',views.remove_cart_item,name='remove_cart_item'),
]
