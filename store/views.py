from tokenize import Number
from django.shortcuts import render,get_object_or_404

from category.models import Category
from .models import Product


def store(request,category_slug=None):
    categories=None
    products=None
    if category_slug != None:
        categories=get_object_or_404(Category,slug=category_slug)
        products=Product.objects.filter(category=categories,is_available=True)
        products_count=products.count()
    else:
        products=Product.objects.all().filter(is_available=True)
        products_count=products.count()
    return render(request,'store/store.html',{'products':products,'products_count':products_count})

def product_detail(request,category_slug,product_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)  # __ is the syntax to get access to the slug of that model
    except Exception as e:
        raise e
    return render(request,'store/product_detail.html',{'single_product':single_product})
