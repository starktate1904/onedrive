from django.urls import path
from . import views

app_name = 'products'  # Define the namespace for URL reversal

urlpatterns = [

    #  products management routes
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/update/',views.product_update, name='product_update'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('upload_products_csv/', views.upload_products_csv, name='upload_products_csv'),
    path('upload_products_csv/product_list/', views.product_list, name='product_list'),


   

    
]