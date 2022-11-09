from email.policy import default
from random import choices
from sys import maxsize
from django.db import models
from accounts.models import Account
from store.models import Product,variation

class Payment(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    payment_id=models.CharField(max_length=260)
    payment_method=models.CharField(max_length=150)
    amount_paid=models.CharField(max_length=100)
    status=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id

class Order(models.Model): 
    STATUS=(
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
    )   
    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    order_number=models.CharField(max_length=100)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    phone=models.CharField(max_length=50)
    email=models.EmailField(max_length=100)
    address_line_1=models.CharField(max_length=50)
    address_line_2=models.CharField(max_length=50,blank=True)
    country=models.CharField(max_length=40)
    state=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    order_note=models.TextField(blank=True)
    order_total=models.FloatField()
    tax=models.FloatField()
    status=models.CharField(max_length=30,choices=STATUS,default='New')
    ip=models.CharField(max_length=50,blank=True)
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    #combine first name and last name
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    #combine address line 1 and line 2
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
         return self.first_name

class OrderProduct(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variations=models.ManyToManyField(variation,blank=True)
    quantity=models.PositiveIntegerField()
    product_price=models.FloatField()
    ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
    
    def total_price(self):
        return self.product_price*self.quantity
    
    def product_tax(self):
        return (self.product_price*self.quantity)*0.06

    
