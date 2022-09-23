from django.db import models
from store.models import Product,variation

class Cart(models.Model):
    #adding only two field
    cart_id=models.CharField(max_length=300,blank=True)
    date_added=models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variations=models.ManyToManyField(variation,blank=True) #many product can have same variation,right?
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.product.product_name

    def sub_total(self):
        return self.product.price * self.quantity
    
    

