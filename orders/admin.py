from django.contrib import admin
from .models import Payment,Order,OrderProduct
from .models import Order,Payment,OrderProduct

class OrderProductInline(admin.TabularInline):
    model=OrderProduct
    extra=0 #in  fact django will provide 5, but with extra =0. they will provide number of item
    #in order to made it only read only and non-editable
    readonly_fields=('payment','user','product','quantity','product_price','ordered')

class Nobi(admin.ModelAdmin):
    #list_display just display, unable to become link
    list_display=('user','full_name','phone','email','order_number','city','order_total','tax','status','is_ordered','created_at')
    list_filter=['status','is_ordered'] #you know what list_filter? at the right side of admin panel site, there a box there, it will showed out something let you filter
    search_fields=['order_number','first_name','last_name','phone','email']
    list_per_page=20
    inlines=[OrderProductInline]

admin.site.register(Payment)
admin.site.register(Order,Nobi)
admin.site.register(OrderProduct)
