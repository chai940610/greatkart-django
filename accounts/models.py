from tkinter.tix import Tree
from django.db import models
#two things need to create own admin page
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
# Create your custom admin page
from django.core.exceptions import ValidationError

#create model for superadmin
class MyAccountManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError('Email address is invalid')
        if not username:
            raise ValueError('User must have an username')
        user=self.model(    #here no phone number, so can add it thru views.py
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,first_name,last_name,email,username,password):
        #using create_user method to create super user
        user=self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin=True  #all these term cannot modify must remember
        user.is_active=True
        user.is_staff=True
        user.is_superadmin=True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    username=models.CharField(max_length=200,unique=True)
    email=models.EmailField(unique=True)
    phone_number=models.CharField(max_length=200)
    #mandatory
    date_joined=models.DateTimeField(auto_now_add=True)
    last_login=models.DateTimeField(auto_now=True)
    is_admin=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    is_superadmin=models.BooleanField(default=False)

    #loginfield
    USERNAME_FIELD='email'  #we will be able login with email
    REQUIRED_FIELDS=['username','first_name','last_name']

    objects=MyAccountManager()

    #create a full name function
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    #this one is 100% when we create custom user model, just memorize
    def has_perm(self,perm,obj=None):
        return self.is_admin    #this mean if the user is admin, he/she has the permission to access all things and do any changes
    
    def has_module_perms(self,add_label):
        return True
    


