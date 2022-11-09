from datetime import datetime
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from carts.models import Cart,CartItem
from .forms import OrderForm
from .models import Order,OrderProduct,Payment
import datetime
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
#remember that place order function need user to login
def place_order(request):
    # we need to verify whether the cart have item or not, if the cart have no item, the link will automatically send back to the store page
    current_user=request.user
    #if the cart count is less than or equal to 0, then redirect back to store page
    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()    # understand this? means see how many cart item insde the cart
    if cart_count <=0:
        return redirect('store')
    #assign some variable make sure they are zero
    grand_total=0
    tax=0
    quantity=0
    total=0
    for cart_item in cart_items:
        total+=(cart_item.product.price* cart_item.quantity)
        quantity+=cart_item.quantity
        print(cart_item.product)
        print(cart_item.quantity)
        print(total)
        # made the tax static, you can made it dynamic in another way
    tax=(total/100)*6
    grand_total=tax+total
    print(total)
    #this one is the checkout page the fill in form all details    
    if request.method=="POST":
        form=OrderForm(request.POST)    #this OrderForm create via forms.py
        if form.is_valid():
            #store all the billing information inside our database
            data=Order()
            # remember cleanned data always need square bracket
            data.user=current_user
            data.first_name=form.cleaned_data['first_name']
            data.last_name=form.cleaned_data['last_name']
            data.email=form.cleaned_data['email']
            data.phone=form.cleaned_data['phone']
            data.address_line_1=form.cleaned_data['address_line_1']
            data.address_line_2=form.cleaned_data['address_line_2']
            data.city=form.cleaned_data['city']
            data.state=form.cleaned_data['state']
            data.country=form.cleaned_data['country']
            data.order_note=form.cleaned_data['order_note']
            data.order_total=grand_total
            data.tax=tax
            data.ip=request.META.get('REMOTE_ADDR') #this will give you the user IP
            data.save() #once the data models been saved, it will create a primary key
            # generate order number
            year=int(datetime.date.today().strftime('%Y'))
            day=int(datetime.date.today().strftime('%d'))
            month=int(datetime.date.today().strftime('%m'))
            date=datetime.datetime(year=year,month=month,day=day)   #remember this method, this can adjust the date system
            current_date=date.strftime("%d%m%Y")    # generate the invoice ID thru date, example 1029102022
            order_number=current_date+str(data.pk)  #since we did data.save() in line 47, so this will save into databse. then will provide ID number
            data.order_number=order_number
            data.save()
            order=Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context={
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }
            return render(request,'orders/payments.html',context)
        else:
            return redirect('checkout')
    else:
        return redirect('checkout')
        
def payments(request):
    body=json.loads(request.body)   
    order=Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])
    print(body) #all the body parts from payments.html will print out when you successfully made a payment
    # store transaction details inside payment models
    payment=Payment(
        user=request.user,
        payment_id=body['transID'],     #the transID inside the body
        payment_method=body['payment_method'],
        amount_paid=order.order_total,    #this not get from the browser, this get from order
        status=body['status'],
    )
    payment.save()
    # we need to update the payment models in Order models after the transaction done, all the info had been updated
    order.payment=payment
    order.is_ordered=True
    order.save()
    #store the product and reduce the quantity once the order been done
    #move the cart item to Order Product table
    cart_item=CartItem.objects.filter(user=request.user)
    #since we have the cart_item we have to loop thru the cart_item
    for item in cart_item:
        orderproduct=OrderProduct()
        orderproduct.order_id=order.id  #due this is foreign key we can call as order_id
        orderproduct.payment=payment
        orderproduct.user_id=request.user.id
        orderproduct.product_id=item.product.pk
        orderproduct.quantity=item.quantity
        orderproduct.product_price=item.product.price
        orderproduct.ordered=True   #after transaction done this need to be checked
        orderproduct.save()
        #IMPORTANT, why there is no variation? because it is manytomanyfield, we can't do it simply with ordrproduct.variations=item.variations, it will error, why? because many to many fields have object and value, what is object and value? example Size(object):XL(value)
        #variation
        cart_item1 =CartItem.objects.get(id=item.id)    #access the CartItem through the id, because we need take the variation
        product_variation=cart_item1.variations.all()
        orderproduct1=OrderProduct.objects.get(id=orderproduct.id)  #orderproduct have id because we did orderproduct.save() in line 108
        orderproduct1.variations.set(product_variation) #the product_variation in line 112 put inside the orderproduct1
        orderproduct1.save()    #as you can see the variation has been set in the admin page

    #Reduce the quantity of sold products
        product=Product.objects.get(pk=item.product.id)
        product.stock-=item.quantity
        product.save()
    #clear the cart
    CartItem.objects.filter(user=request.user).delete() #delete the cart item after transaction made
    #send order email to customer
    mail_subject="Thank you for your order"
    message=render_to_string('orders/order_receive_email.html',{
                'user':request.user,   #default_token_generator generate token for the user
                'order':order,
    })
    to_email=request.user.email
    send_email=EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()
    #send order number and transaction id back to sendData method in Script side via JsonResponse
    data={
        'order_number':order.order_number,
        'transID':payment.payment_id,
    }
    return JsonResponse(data)

def order_complete(request):
    sub_total=0
    #GET from URL, kindly look thru URL will solve everything
    order_number=request.GET.get('order_number')
    transID=request.GET.get('payment_id')
    try:
        order=Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_products=OrderProduct.objects.filter(order_id=order.id)
        payment=Payment.objects.get(payment_id=transID)
        for i in ordered_products:
            sub_total+=i.product_price*i.quantity
        return render(request,'orders/order_complete.html',{'sub_total':sub_total,'order':order,'ordered_products':ordered_products,'order_number':order.order_number,'transID':payment,})
    except(Payment.DoesNotExist,Order.DoesNotExist): #handle payment doesn't exist and order doesn't exist error, means you directly type order_complete in URL, they will redirect you to the homepage
        return redirect('home')
    
    #Tips of the day, do you know the differences between get and filter method
    #mostly get method is applied to look for single item, meanwhile filter is use to find mutiple item