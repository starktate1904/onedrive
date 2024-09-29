from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    
    path('admin/', admin.site.urls),
    path('', include('auth_pos.urls')),
    path('products/', include('products.urls')),
    path('branches/', include('branches.urls')),
    path('sale/', include('sale.urls')),
    path('staff/', include('staff.urls')),
    path('profile/', include('user_profile.urls'))


]
