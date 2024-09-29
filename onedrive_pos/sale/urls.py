from . import views
from django.urls import path



app_name = 'sales'  # Define the namespace for URL reversal


urlpatterns = [

    
  

    path('products/', views.products_list_view, name='products_list'),
       # Sales list AJAX URL
    path('sales/', views.sales_list_view, name='sales_list'),
    # Product options AJAX URL
    path('products/', views.get_product_view, name='get_products'),
    path('products/search', views.search_products_view, name='search-products'),
    # Add sale AJAX URL
    path('sales/add/', views.add_sale, name='add_sale'),
    path('sales/create/', views.sales_create_view, name='create_sale'),
    # Sales detail AJAX URL
    path('sales/<pk>/', views.sales_detail, name='sales_detail')


]