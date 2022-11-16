from ast import Or
from django.http import HttpResponse
from tokenize import Number
from django.shortcuts import render,get_object_or_404,redirect
from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from .models import Product,ReviewRating
from carts.models import Cart,CartItem
#paginator tools
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
#search tools need to search mutiple things at the same time
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct

def store(request,category_slug=None):
    categories=None
    products=None
    if category_slug != None:
        categories=get_object_or_404(Category,slug=category_slug)
        products=Product.objects.filter(category=categories,is_available=True)
        paginator=Paginator(products,5)
        page=request.GET.get('page')
        paged_product=paginator.get_page('page')
        products_count=products.count()
    else:
        products=Product.objects.all().filter(is_available=True).order_by('id')
        #paginator
        paginator=Paginator(products,5)
        page=request.GET.get('page')    #get the page from URL
        paged_product=paginator.get_page(page)  #that 6 products will store in paged_product
        products_count=products.count()
    return render(request,'store/store.html',{'products':paged_product,'products_count':products_count})

def product_detail(request,category_slug,product_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)  # __ is the syntax to get access to the slug of that model
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()  # cart__ mean check the cart model, because cart is foreign key of Cart, so cart__ check the cart model then go to cart id
        # return HttpResponse(in_cart)    #it will return true or false, if true mean this product exist in any cart
        # exit()
    except Exception as e:
        raise e
        #check whether the user purchase this item before or not
    if request.user.is_authenticated:
        try:
            orderproduct=OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()   #check this person buy this item before or not
        except OrderProduct.DoesNotExist:
            orderproduct=None
    else:
        orderproduct=None
    #get all the reviews
    reviews=ReviewRating.objects.filter(product_id=single_product.pk,status=True)   #status=false for those review you don't want show out
    return render(request,'store/product_detail.html',{'reviews':reviews,'orderproduct':orderproduct,'single_product':single_product,'in_cart':in_cart})

def testing(request,babi=0):
    cart=Cart.objects.filter(cart_id=_cart_id(request))
    cart_items=CartItem.objects.all().filter(cart=cart[:1]) #In this case, the subquery must only return a single column and a single row: the email address of the most recently created comment
    return render(request,'test.html',{'cart_items':cart_items})

#from this you will found that function based view can do in many templates
def search(request,products=None):
    #receive what is coming from the url
    if 'bird' in request.GET:   #check get this keyword or not
        keyword=request.GET['bird']
        if keyword: #if keyword has something
            products=Product.objects.order_by('-created_date').filter(Q(product_name__icontains=keyword) | Q(description__icontains=keyword))
            products_count=products.count()
    return render(request,'store/store.html',{'products':products,'products_count':products_count,'keyword':keyword})


def submit_review(request,product_id):
    url=request.META.get('HTTP_REFERER')    #to store the previous URL
    if request.method=="POST":
        try:
            #if the review already exist by the user, just updated it
            reviews=ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)  #why need two underscore? because we reference to the ReviewRating user id, so need two underscore
            form=ReviewForm(request.POST,instance=reviews)   #request.POST we will having star, title and everything, why we need instance? because if the review had been created by the user, so we just update the review, if the review never created by the user, the review consider as new
            form.save()
            messages.success(request,'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:   #which mean this is new comment, current user haven't post any comment
            form=ReviewForm(request.POST)
            if form.is_valid():
                data=ReviewRating()
                data.subject=form.cleaned_data['subject']
                data.rating=form.cleaned_data['rating']
                data.review=form.cleaned_data['review']
                data.ip=request.META.get('REMOTE_ADDR') #ADDR is store the IP address
                data.product_id=product_id
                data.user_id=request.user.id
                data.save()
                messages.success(request,'Thank you! Your review has been submitted.')
                return redirect(url)