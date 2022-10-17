from dataclasses import fields
from logging import PlaceHolder
from tkinter.tix import INTEGER
from unicodedata import digit
from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Password'
    }))    #due to password field
    confirm_password=forms.CharField(widget=forms.PasswordInput({
        'placeholder':'Repeat Password'
    }))
    phone_number=forms.CharField(widget=forms.NumberInput({ #numberinput had overwrite the models.py attribute
        'placeholder':'Enter Phone Number'
    }))
    class Meta:
        model=Account
        #for field in self.fields:, the field is first_name,last_name .....xxx
        fields=['first_name','last_name','email','phone_number','password'] #no put username due we want to generate username automatically thru email

    def __init__(self,*args,**kwargs):  # to overwrite the functionality of this form
        super().__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']='Enter Last Name'
        self.fields['email'].widget.attrs['placeholder']='Enter Email'
        
        #loop all the field and given the equal attribute
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control' #what is this mean, it will inject all the field with form-control, this is very creative

#check for two password whether same or not? if both password are different, user unable to created
    #from the lecture say, super is something like modify something what Django given
    def clean(self):
        cleanned_data=super(RegistrationForm,self).clean()
        password=cleanned_data.get('password')
        confirm_password=cleanned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )
    
    