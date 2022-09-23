from django.contrib import admin
from .models import Cart,CartItem

class CartAdmin(admin.ModelAdmin):
     list_display=['product','cart','quantity','is_active']

class asura(admin.ModelAdmin):
     list_display=['cart_id','date_added']

admin.site.register(Cart,asura)
admin.site.register(CartItem,CartAdmin)
