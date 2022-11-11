from django.db import models
from django.urls import reverse
from category.models import Category
from accounts.models import Account

class Product(models.Model):
    product_name=models.CharField(max_length=200,unique=True)
    slug=models.SlugField(max_length=200,unique=True)
    description=models.TextField(blank=True)
    price=models.FloatField()
    images=models.ImageField(upload_to='photos/products')
    stock=models.PositiveIntegerField()
    is_available=models.BooleanField(default=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)   #once the category been deleted, the product also will deleted
    created_date=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    def get_url(self):
        return reverse('products_detail',args=[self.category.slug,self.slug])

class variationmanager(models.Manager):
    def colour(self):
        return super(variationmanager,self).filter(variation_category='colour',is_active=True)
    
    def size(self):
        return super(variationmanager,self).filter(variation_category='size',is_active=True)

    #tips of the day: super(variationmanager,self)=super()
    def length(self):
        return super().filter(variation_category='length',is_active=True)

variation_category_choice=(
    ('colour','colour'),    #as you remember that once you change the right side, the whole name will change too in admin page
    ('size','size'),
    ('length','logo'),
)

class variation(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=200,choices=variation_category_choice)
    variation_value=models.CharField(max_length=200)
    is_active=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now_add=True)

    objects=variationmanager()  #link the variationmanager to the variation_category, so the colour and sizc

    # def __unicode__(self):
    #     return self.is_active

    def __str__(self):
        return self.variation_value

class ReviewRating(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE) #if the product got deleted, we also need to delete the review as well
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    subject=models.CharField(max_length=200,blank=True)
    review=models.TextField(blank=True)
    rating=models.FloatField()
    ip=models.CharField(max_length=100,blank=True)
    status=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    