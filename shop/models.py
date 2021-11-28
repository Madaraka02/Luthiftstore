from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import RegexValidator

# Create your models here.


class Customer(models.Model):
    user = models.OneToOneField(User, null=False, blank=False, on_delete=models.CASCADE)
    # CUSTOM FIELD
    phone_number = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100)
   

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__ (self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    new_price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to='static/images')
    old_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    slug = models.SlugField()
    description = models.TextField()
    featured = models.BooleanField(default=False)

    def __str__ (self):
        return self.name

    def get_product_discount(self):
        discount = self.old_price - self.new_price 
        save = discount * 100
        discount_percentage = save // self.old_price 
        return discount_percentage

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={'slug':self.slug}) 


    def get_remove_from_cart_url(self):
        return reverse('remove_from_cart', kwargs={'slug':self.slug})

    def get_remove_single_item_from_cart_url(self):
        return reverse('remove_single_item_from_cart', kwargs={'slug':self.slug})         
   
class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/images', blank=True, null=True)

    def __str__(self):
        return self.product.name        
    class Meta:
        verbose_name_plural = 'ProductImages'   

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    ordered = models.BooleanField(default=False)    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)   

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def get_total_item_price(self):
        return self.quantity * self.product.new_price

    def get_final_price(self):
        return self.get_total_item_price()        

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey("Payment", on_delete=models.SET_NULL, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
       
    def get_items(self):
        # return "\n".join([i.item for i in self.items.all()])
        return ",".join([str(i) for i in self.items.all()])

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total        


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mpesa_phone_number =  PhoneNumberField(null=True)
    mpesa_name = models.CharField(max_length=500, null=True)
    delivery_address = models.CharField(max_length=500, null=True)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return self.user.username


class Contact(models.Model):
    email = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.email        

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    charge_id = models.CharField(max_length=100)
    amount = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username     