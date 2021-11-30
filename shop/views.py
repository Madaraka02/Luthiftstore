from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.generic import View, DetailView, ListView
from shop.models import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient
import requests
from requests.auth import HTTPBasicAuth
import json
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
from shop.forms import *

# Create your views here.

def home(request):
    products = Product.objects.all().order_by('-id')[:12]
    categories = Category.objects.all().order_by('-id')
    featured = Product.objects.filter(featured=True).order_by('-id')[:12]
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
    context = {
        'products':products,
        'categories': categories,
        'featured':featured,
        'form':form
    }
    return render(request, 'shop/index.html', context)

def store(request):
    products = Product.objects.all().order_by('-id')
    paginator = Paginator(products, 18)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj':page_obj
    }
    return render(request, 'shop/store.html', context)    

def details(request, id):
    item = Product.objects.get(id=id)
    related = Product.objects.filter(category=item.category).exclude(id=id)[:4]
    context = {
        'item': item,
        'related': related
    }
    return render(request, 'shop/product.html', context)

@login_required
def admin(request):
    if request.user.is_staff:
        prod_count = Product.objects.all().count()
        order_count = Order.objects.all().count()
        category_count = Category.objects.all().count()
        message_count = Contact.objects.all().count()

        context = {
            'prod_count':prod_count,
            'order_count':order_count,
            'category_count':category_count,
            'message_count':message_count,
        }
        return render(request, 'admin/main.html', context)
    return redirect('home')    

def adminProducts(request):
    if request.user.is_staff:
        item_list = Product.objects.all().order_by('-id')
        page = request.GET.get('page', 1)

        paginator = Paginator(item_list, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)

        form = ProductForm()

        if request.method == "POST":
            form = ProductForm(request.POST, request.FILES)
            # files = request.FILES.getlist('more_product_images')
            
            if form.is_valid():  
                form.save()
                # item = form.save() 
                # for f in files:
                #     item_image = ProductImages(product=item, image=f)
                #     item_image.save()
                # return redirect('shadmin')    
        context = {
            'items': items,
            'form':form,
        }
        return render(request, 'admin/products.html', context)  

def adminCategories(request):
    if request.user.is_staff:
        item_list = Category.objects.all().order_by('-id')
        page = request.GET.get('page', 1)

        paginator = Paginator(item_list, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)

        form = CategoryForm()

        if request.method == "POST":
            form = CategoryForm(request.POST, request.FILES)
            
            if form.is_valid():  
                form.save() 
                return redirect('shadmin')
        context = {
            'items': items,
            'form':form,
        }
        return render(request, 'admin/categories.html', context)   

def adminOrders(request):
    if request.user.is_staff:
        item_list = Order.objects.all().order_by('-id')
        page = request.GET.get('page', 1)

        paginator = Paginator(item_list, 15)
        try:
            buys = paginator.page(page)
        except PageNotAnInteger:
            buys = paginator.page(1)
        except EmptyPage:
            buys = paginator.page(paginator.num_pages)
        context = {
            'buys': buys,
        }
    return render(request, 'admin/orders.html', context) 

def adminMessages(request):
    if request.user.is_staff:
        applications = Contact.objects.all().order_by('-id')
        #paginate applications
            
        paginator = Paginator(applications, 4)
        page_number = request.GET.get('page')
        application_obj = paginator.get_page(page_number) 
        page = request.GET.get('page', 1)

        context = {
            'application_obj': application_obj,
        }
    return render(request, 'admin/messages.html', context)           
    
class catlistView(ListView):
    template_name = "shop/blank.html"
    context_object_name = 'catlist'
    # paginate_by = 3

    def get_queryset(self):
        content = {
            'cat': self.kwargs['category'],
            'items': Product.objects.filter(category__name=self.kwargs['category'])
        }
        return content    

@login_required       
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(product=product, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
       
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=product.slug).exists():
            order_item.quantity +=1
            order_item.save()
            messages.success(request, f"{product.name}'s was updated")
            return redirect('cart')
        else:
            order.items.add(order_item)
            order.save()
            messages.success(request, f"{product.name} was added to your cart")
            return redirect('cart')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered=False, ordered_date=ordered_date)
        order.items.add(order_item)
        order.save()
        messages.success(request, f"{product.name} was added to your cart")
        return redirect('cart') 

class cartView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, 'shop/cart.html', context)  

def search(request):
    q = request.GET['q']
    if q:
        context = {
            'data' : Product.objects.filter(name__icontains=q).order_by('-id'),
        }

        return render(request, 'shop/search.html', context)
    return redirect('store')      

@login_required          
def remove_from_cart(request, slug):  
    product = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(product=product, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=product.slug).exists():
            order.items.remove(order_item)
            order.save()
            messages.success(request, f"{product.name} was removed from your cart")
            return redirect('cart')
        else:
            messages.info(request, f"{product.name} was not in your cart")
            return redirect('cart') 
    else:
        messages.info(request, "You dont have any items in your cart")
        return redirect('products')      

@login_required
def remove_single_item_from_cart(request, slug):  
    product = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(product=product, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=product.slug).exists():
            if order_item.quantity > 1:
                order_item.quantity -=1
                order_item.save()
            else:
                order.items.remove(order_item)
                order.save()   
            return redirect('cart')
        else:
            messages.info(request, f"{product.name} was not in your cart")
            return redirect('cart') 
    else:
        messages.info(request, "You dont have any items in your cart")
        return redirect('products')       

class checkoutView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = DeliveryForm()
        context = {
            'form': form,
            'order': order,
        }
        return render(self.request, 'shop/checkout.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = DeliveryForm(self.request.POST or None)
        if form.is_valid():
            deliver = form.save(commit=False)

            # mpesa_phone_number = form.cleaned_data.get('mpesa_phone_number')
            # mpesa_name = form.cleaned_data.get('mpesa_name')
            # delivery_address = form.cleaned_data.get('delivery_address')

            address = Address(
                user = self.request.user,
                mpesa_phone_number = deliver.mpesa_phone_number,
                mpesa_name = deliver.mpesa_name,
                delivery_address = deliver.delivery_address,
            )
            address.save()
            order.address = address
            order.save()
            
            print(form.cleaned_data)
            messages.success(self.request, "Your order has been received we will respond within 24 hours")
            return redirect('payment')
        else:
            print(f'form_invalid') 
            return redirect('checkout')  

def deleteProduct(request, id):
    product = Product.objects.get(id=id)
    product.delete()

    return redirect ('admproducts')


def updateProduct(request, id):
    product = Product.objects.get(id=id)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('admproducts')
    context ={
        'product': product,
        'form': form

    }
    return render(request, 'admin/update-products.html', context)


def deleteCategory(request, id):
    category = Category.objects.get(id=id)
    category.delete()

    return redirect ('admcategories')


def updateCategory(request, id):
    category = Category.objects.get(id=id)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('admcategories')
    context ={
        'category': category,
        'form': form

    }
    return render(request, 'admin/update-categoriess.html', context)

def deleteOrder(request, id):
    order = Order.objects.get(id=id)
    order.delete()

    return redirect ('admorders')

def deleteMessage(request, id):
    message = Contact.objects.get(id=id)
    message.delete()

    return redirect ('admmessages')


def payment_complete(request):
    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user, ordered=False, id=body['orderID'])
    payment = Payment(
        user=request.user,
        charge_id=body['payID'],
        amount=order.get_total()
    )
    payment.save()

    # assign the payment to order
    order.payment = payment
    order.ordered = True
    order.save()
    messages.success(request, "Payment was successful")
    return redirect('home')


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)

        context = {
            'order': order,

        }
        return render(self.request, 'shop/payment.html', context)


def getAccessToken(request):
    consumer_key = 'snymkrCA9v75JsGwlyCPhdyg1YcZH9Ed'
    consumer_secret = 'T7Ldy6sVMhpp8UKw'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    return HttpResponse(validated_mpesa_access_token)    

def lipa_na_mpesa_online(request):
    order = Order.objects.get(user=request.user, ordered=False)
    # remove "+" from customer's phone number
    phone = str(order.address.mpesa_phone_number).translate({ord('+'): None})

    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline", #CustomerBuyGoodsOnline
        "Amount": int(order.get_total()), 
        "PartyA": int(phone),  # replace with your phone number to get stk push...convert phone number to integer
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": int(phone),  # replace with your phone number to get stk push .translate({ord('+'): None})
        "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
        "AccountReference": "LU THRIFT SHOP",
        "TransactionDesc": "Testing stk push"
    }
    response = requests.post(api_url, json=request, headers=headers)
    
    return HttpResponse('Payment details sent')    