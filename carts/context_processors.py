from .models import Cart,CartItem
from .views import _cart_id
from django.http import HttpResponse

def counter(request):
    cart_count=0
    if 'admin' in request.path: #if admin are in the url, then return blank
        return {}
    else:
        try:
            cart=Cart.objects.filter(cart_id=_cart_id(request))
            cart_items=CartItem.objects.all().filter(cart=cart[:1]) #start from 1
            for abc in cart_items:
                cart_count += abc.quantity
        except Cart.DoesNotExist:
            cart_count=0
    return dict(cart_count=cart_count)