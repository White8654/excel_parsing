from django.urls import path
from . import views

urlpatterns = [

    path('products/', views.product_list, name='product_list'),  #api for fetching data of all the products
    path('', views.product_list_view, name='product_list_view'), #route to serve product listing html page
    path('upload-products/', views.upload_products, name='upload_products'), #route to serve upload products html page
]
