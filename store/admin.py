from django.contrib import admin
from .models import Product,variation

class babi(admin.ModelAdmin):
    prepopulated_fields={'slug':('product_name',)}
    list_display=('product_name','price','stock','category','modified_date','is_available')

class dummy(admin.ModelAdmin):
    list_display=('product','variation_category','variation_value','is_active')
    #I want to edit the is_active from admin page without enter inside
    list_editable=('is_active',)    #must comer
    list_filter=('product','variation_category','variation_value')

admin.site.register(Product,babi)
admin.site.register(variation,dummy)

