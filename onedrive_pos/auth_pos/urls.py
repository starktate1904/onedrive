
from django.urls import path
from . import views
app_name = 'auth_pos'  # Define the namespace for URL reversal


urlpatterns = [


#  authentication routes
    path('register/',views.register, name = 'register'),
    path('',views.login, name= 'login'),
    path('logout/',views.logout_user, name= 'logout'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('manager_dashboard', views.manager_dashboard, name='manager_dashboard'),
    path('cashier_dashboard', views.cashier_dashboard, name='cashier_dashboard'),


    
   
   


   
    
]