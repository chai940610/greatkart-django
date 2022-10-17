from email import message
from http.client import HTTPResponse
from django.shortcuts import render,redirect
from django.contrib import messages,auth
from accounts.models import Account
from .forms import RegistrationForm
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def register(request):
    if request.method=="POST":
        form=RegistrationForm(request.POST) #request.POST contain with the details
        if form.is_valid():
            #since we are using the django form, so we need the cleanned value to fetch the data
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']  #no need taken the confirm password, the rathar kumar say he will show me how to validate
            username=email.split("@")[0]    # 0 is left side
            #create user, go to accounts.models.py AccountBaseManager, look for create_user that one, then you will understand
            user=Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)  #this create_user is from django authentication model
            #due to phone number is not in the accounts.models.py, AccountBaseManager, create_user function, so we add it here
            user.phone_number=phone_number
            user.save()
            # user activation
            current_site=get_current_site(request)
            mail_subject="Please activate your account"
            message=render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  #encode the primary key
                'token':default_token_generator.make_token(user)    #default_token_generator generate token for the user
            })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            # messages.success(request,'Thank you for registering with us. We have sent you a verification email to your email address. Please verify it.')    #this is the message information
            return redirect('/accounts/login/?command=verification&email='+email)    #because we have email in our URL, so in login.html, you can use request.GET.email to retrieve it
    else:
        form=RegistrationForm() # GET method
    return render(request,'accounts/register.html',{'form':form})

def login(request):
    if request.method=="POST":
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email,password=password)
        if user is not None:    #mean the email and password are corrected
            auth.login(request,user)
            messages.success(request,'You are now logged in.')
            return redirect('dashboard')
        else:
            messages.error(request,'Invalid login credentials') #mean invalid email and password
            return redirect('login')
    return render(request,'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out.')
    return redirect('login')

def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()  #decode the uidb64
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):  #except mean handling fees errors
        user=None
    if user is not None and default_token_generator.check_token(user,token):    #mean we got the user and check the token
        user.is_active=True
        user.save()
        messages.success(request,'Congratulation! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')

def forgotpassword(request):
    if request.method=='POST':
        email=request.POST['email'] #this email is coming from accounts/forgotpassword.html email
        if Account.objects.filter(email=email).exists():   #kindly check this email whether exists or not, the result will be true or false
            user=Account.objects.get(email__exact=email)    #exact mean check the email address is same in the database or not
            #Reset Password email
            current_site=get_current_site(request)
            mail_subject="Reset your password"
            message=render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  #encode the primary key
                'token':default_token_generator.make_token(user)    #default_token_generator generate token for the user
            })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            messages.success(request,'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist!')
            return redirect('forgotpassword')

    return render(request,'accounts/forgotpassword.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()  #decode the uidb64
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):  #except mean handling fees errors
        user=None
    if user is not None and default_token_generator.check_token(user,token):    
        request.session['uid']=uid
        messages.success(request,'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request,'This link has been expired')
        return redirect('login')

def resetpassword(request):
    if request.method=="POST":
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password == confirm_password:
            #get the uid from the session
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(confirm_password) #have to use set_password, set_password is the in built function of django
            user.save()
            messages.success(request,'Password reset successful')
            return redirect('login')
        else:
            messages.error(request,'Password do not match!')
            return redirect('resetpassword')
    else:
        return render(request,'accounts/resetpassword.html')