from django import forms
from django.forms import ModelForm
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from shop.models import *



class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

        
class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'        

class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'                

class AddressForm(forms.Form):
    mpesa_phone_number = PhoneNumberField()
    # mpesa_phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$')
    # mpesa_phone_number = PhoneNumber.from_string(phone_number=raw_phone, region='KE').as_e164
    # mpesa_phone_number = PhoneNumberField(widget=PhoneNumberPrefixWidget(initial='KE'))
    mpesa_name = forms.CharField(required=False)
    delivery_address = forms.CharField(required=False)

class DeliveryForm(ModelForm):
    class Meta:
        model = Address
        fields = ('mpesa_phone_number', 'mpesa_name', 'delivery_address')    