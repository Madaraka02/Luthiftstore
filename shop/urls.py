from django.urls import path

from .views import *


urlpatterns = [
    path('', home, name="home"),
    path('shadcore/admin/', admin, name="shadmin"),
    path('shadcore/admin/products/', adminProducts, name="admproducts"),
    path('shadcore/admin/categories/', adminCategories, name="admcategories"),
    path('shadcore/admin/orders/', adminOrders, name="admorders"),
    path('shadcore/admin/messages', adminMessages, name="admmessages"),
    path('shop/', store, name="store"),
    path('cart/', cartView.as_view(), name="cart"),
    path('category/<category>/', catlistView.as_view(), name='category_products'),
    path('add_to_cart/<str:slug>', add_to_cart, name="add_to_cart"),
    path('details/<int:id>/', details, name='details'),
    path('search/', search, name='search'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('remove-single-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('checkout/', checkoutView.as_view(), name='checkout'),
    path('payment/mpesa/', PaymentView.as_view(), name='payment'),
    path('payment-complete', payment_complete, name="payment_complete"),
    path('shadcore/admin/update/product/<int:id>/', updateProduct, name='update_product'),
    path('shadcore/admin/delete/procuct/<int:id>/', deleteProduct, name='delete_product'),
    path('shadcore/admin/update/category/<int:id>/', updateCategory, name='update_category'),
    path('shadcore/admin/delete/category/<int:id>/', deleteCategory, name='delete_category'),
    path('shadcore/admin/delete/message/<int:id>/', deleteMessage, name='delete_message'),
    path('shadcore/admin/delete/order/<int:id>/', deleteOrder, name='delete_order'),
    path('access/token/', getAccessToken, name='get_mpesa_access_token'),
     path('online/lipa/', lipa_na_mpesa_online, name='lipa_na_mpesa'),
    # path('daraja/stk-push/', stk_push_callback, name='mpesa_stk_push_callback'),
]