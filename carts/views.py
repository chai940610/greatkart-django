import re
from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

def cart(request,total=0,quantity=0,cart_items=None,tax=0,grand_total=0):
    try:
        #check whether is the user is login or not, if the user is login, the cart automatically check this user add to cart or not
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)    #request.user means current user
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total+=(cart_item.product.price* cart_item.quantity)
            quantity+=cart_item.quantity
        tax=(total/100)*6
        grand_total=total + tax
    except ObjectDoesNotExist:
        pass # just ignore
    return render(request,'store/cart.html',{'total':total,'quantity':quantity,'cart_items':cart_items,'tax':tax,'grand_total':grand_total})

def add_cart(request,product_id):
    current_user=request.user
    product=Product.objects.get(id=product_id)  #get the product, every product have an ID
    #if the user is authenticated
    if current_user.is_authenticated:
        #made a list of production variation
        product_variation=[]    #assign product variation to 0
        if request.method=="POST":
            for item in request.POST:
                key=item    #remember that the item is the name, not the answer
                value=request.POST[key]
                # print(key,value)
                #understand how all these work?
                #1) for item in request.POST: , get all the item from the <form> in product_detail.html, which is method POST, and you found that the select icon and the CSRF will occur
                #print(key,value) the results shows out the CSRF token,the colour variation, size, all these data will occured because you select something, once you select something and thru POST method, all these will print out
                try:
                    variation1=variation.objects.get(variation_category__iexact=key,variation_value__iexact=value)  #understand how this work? once you search the POST method thru the product_detail.html <form> things, then the key will all go inside the variation_category, then value will go to variation_value, then iexact means find any of them match each other or not? if matched, then grab it
                    # print(variation1)
                    product_variation.append(variation1)    #do you know what append means? means link something to the object
                    print(product_variation)
                except:
                    pass
                #post anything from the POST request,for my study, just for loop will occur
        
        
        is_cart_item_exists=CartItem.objects.filter(product=product,user=current_user).exists() #the answer will be either True or False
        if is_cart_item_exists: #okay, let check the CartItem models inside, see whether inside got what item
        # try:
            # cart_item=CartItem.objects.get(product=product,cart=cart)   #these product and cart are taken from above
            cart_item=CartItem.objects.filter(product=product,user=current_user)
            #existing variations, take it from database
            #current variation, get from product variation above
            #item id, take from database
            #check the current variation is inside the existing variation, it mean is the current variation in the cart or not, if yes, then increase the quantity of the cart item
            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variation=item.variations.all()
                # ex_var_list.append(existing_variation)    #we have to convert it into list/query
                ex_var_list.append(list(existing_variation))    #retrieve all the existing variation in list into ex_var_list
                id.append(item.id)  #retrieve all the ID from the CartItem into the ID
            # print(id)
            print(ex_var_list)
            #so now check the product variation is in the current variation, ex_var_list
            if product_variation in ex_var_list:    #the current variation is being inside the database or not, if exist will occur true, if no will false
                #increase cart item quantity
                #as you remember that every models have their own ID, also known as pk
                index=ex_var_list.index(product_variation)
                # print(index)
                item_id=id[index]
                # print(item_id)
                item=CartItem.objects.get(product=product,pk=item_id)
                item.quantity+=1
                item.save()
            else:
                #create a new cart item, if the variation is not in the cart item
                item=CartItem.objects.create(product=product,quantity=1,user=current_user)
                #now check the product_variation is empty or not
                #check the length of the object
                if len(product_variation)>0:
                    item.variations.clear()    #clear the variation first
                    item.variations.add(*product_variation)
                # cart_item.quantity+=1   #when someone tekan add to cart this function, quantity will increase by 1
                item.save()
        else:
        # except CartItem.DoesNotExist: old method
            cart_item=CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation)>0: #mean the production variation not empty
                cart_item.variations.clear()    #clear the variation first
                cart_item.variations.add(*product_variation)  #this line of code extremely important, add variation in cart item of admin page, first, you import the variation model to this carts.views.py, then add all these variation
            cart_item.save()
        # return HttpResponse(cart_item.product)
        # exit()
        return redirect ('cart')
    # else means no user login
    else:   #if user is not authenticated
        #made a list of production variation
        product_variation=[]    #assign product variation to 0
        if request.method=="POST":
            for item in request.POST:
                key=item    #remember that the item is the name, not the answer
                value=request.POST[key]
                # print(key,value)
                #understand how all these work?
                #1) for item in request.POST: , get all the item from the <form> in product_detail.html, which is method POST, and you found that the select icon and the CSRF will occur
                #print(key,value) the results shows out the CSRF token,the colour variation, size, all these data will occured because you select something, once you select something and thru POST method, all these will print out
                try:
                    variation1=variation.objects.get(variation_category__iexact=key,variation_value__iexact=value)  #understand how this work? once you search the POST method thru the product_detail.html <form> things, then the key will all go inside the variation_category, then value will go to variation_value, then iexact means find any of them match each other or not? if matched, then grab it
                    # print(variation1)
                    product_variation.append(variation1)    #do you know what append means? means link something to the object
                    print(product_variation)
                except:
                    pass
                #post anything from the POST request,for my study, just for loop will occur
        #if user is authenticated, the cart code below is no longer needed
        try:
             cart=Cart.objects.get(cart_id=_cart_id(request))    #get the cart by using the cart id present in the session
        except Cart.DoesNotExist:
             cart=Cart.objects.create(
                 cart_id=_cart_id(request)
             )
        cart.save()
        is_cart_item_exists=CartItem.objects.filter(product=product,cart=cart).exists() #the answer will be either True or False
        if is_cart_item_exists: #okay, let check the CartItem models inside, see whether inside got what item
        # try:
            # cart_item=CartItem.objects.get(product=product,cart=cart)   #these product and cart are taken from above
            cart_item=CartItem.objects.filter(product=product,cart=cart)
            #existing variations, take it from database
            #current variation, get from product variation above
            #item id, take from database
            #check the current variation is inside the existing variation, it mean is the current variation in the cart or not, if yes, then increase the quantity of the cart item
            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variation=item.variations.all()
                # ex_var_list.append(existing_variation)    #we have to convert it into list/query
                ex_var_list.append(list(existing_variation))    #retrieve all the existing variation in list into ex_var_list
                id.append(item.id)  #retrieve all the ID from the CartItem into the ID
            # print(id)
            print(ex_var_list)
            #so now check the product variation is in the current variation, ex_var_list
            if product_variation in ex_var_list:    #the current variation is being inside the database or not, if exist will occur true, if no will false
                #increase cart item quantity
                #as you remember that every models have their own ID, also known as pk
                index=ex_var_list.index(product_variation)
                # print(index)
                item_id=id[index]
                # print(item_id)
                item=CartItem.objects.get(product=product,pk=item_id)
                item.quantity+=1
                item.save()
            else:
                #create a new cart item, if the variation is not in the cart item
                item=CartItem.objects.create(product=product,quantity=1,cart=cart)
                #now check the product_variation is empty or not
                #check the length of the object
                if len(product_variation)>0:
                    item.variations.clear()    #clear the variation first
                    item.variations.add(*product_variation)
                # cart_item.quantity+=1   #when someone tekan add to cart this function, quantity will increase by 1
                item.save()
        else:   #if cart item not exists
        # except CartItem.DoesNotExist: old method
            cart_item=CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if len(product_variation)>0: #mean the production variation not empty
                cart_item.variations.clear()    #clear the variation first
                cart_item.variations.add(*product_variation)  #this line of code extremely important, add variation in cart item of admin page, first, you import the variation model to this carts.views.py, then add all these variation
            cart_item.save()
        # return HttpResponse(cart_item.product)
        # exit()
        return redirect ('cart')

def remove_cart(request,babi,bunyi):
    
    product=get_object_or_404(Product,id=babi)
    try:
        if request.user.is_authenticated:
            cart_item=CartItem.objects.get(product=product,user=request.user,pk=bunyi)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))    #this code will run when we are not login
            cart_item=CartItem.objects.get(product=product,cart=cart,pk=bunyi)
        if cart_item.quantity>1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect ('cart')

def remove_cart_item(request,lanli,london):
    product=get_object_or_404(Product,id=lanli)
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(product=product,user=request.user,id=london)
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(product=product,cart=cart,pk=london)
    cart_item.delete()
    return redirect('cart')

@login_required(login_url='login')
def checkout(request,total=0,quantity=0,cart_items=None,tax=0,grand_total=0):
    try:
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)    #request.user means current user
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total+=(cart_item.product.price* cart_item.quantity)
            quantity+=cart_item.quantity
        tax=(total/100)*6
        grand_total=total + tax
    except ObjectDoesNotExist:
        pass # just ignore
    return render(request,'store/checkout.html',{'total':total,'quantity':quantity,'cart_items':cart_items,'tax':tax,'grand_total':grand_total})