from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .models import *
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import datetime
from products.models import *
from sale.models import *
from staff.models import *
from .models import User
from django.contrib.auth import get_user_model
import json
from datetime import date
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, FloatField, F
from django.db.models.functions import Coalesce

User = get_user_model()






# register view 
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
       

        if email =='' or username=='' or password=='':
            return  HttpResponse('Validation Failed')


        if User.objects.filter(username=username, email=email,).exists():
             return render(request,'register.html',{'error':'Username or Email already taken'})
        user = User.objects.create_user(username,password=password,email=email)
        # Create the Employee object after user creation
        Employee.objects.create(user=user,branch=None)  # Link user to the employee
        user.role = 'manager'  # Set the default role
        user.save()

        login(request)
        messages.success(request, 'Registration successful!')

        # Redirect based on user role
        if user.role == 'admin':
            return redirect('auth_pos:admin_dashboard')
        elif user.role == 'manager':
            return redirect('auth_pos:manager_dashboard')
        else:
            return redirect('auth_pos:cashier_dashboard')
       
    else:
        return render(request,'authentication/register.html')


# login_view 
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
       
        user = authenticate(request,username=username,password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Login successful!')

             # Redirect based on user role
            if user.role == 'admin':
                return redirect('auth_pos:admin_dashboard')
            elif user.role == 'manager':
                return redirect('auth_pos:manager_dashboard')
            else:
                return redirect('auth_pos:cashier_dashboard')
        else:
            messages.error(request, 'Invalid credentials')

    return render( request, 'authentication/login.html')


# logut view
@login_required
def logout_user(request):


    return redirect('auth_pos:login')





# admin_dashboard view
@login_required
@user_passes_test(lambda user: user.has_perm('main.view_admin_dashboard'))
def admin_dashboard(request):



      # Get the current time
    current_time = datetime.datetime.now()

    # Determine the greeting based on the time of day
    if current_time.hour < 12:
        greeting = "Good Morning"
    elif current_time.hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening" 

   
    branches_count = Branch.objects.count()
    products_count = Product.objects.count()
    employee_count = Employee.objects.count()
  
    


    context = {
      
       
        'products_count': products_count,
        'branches_count': branches_count,
        'employee_count': employee_count,
        'greeting': greeting,

    }
  
    return render( request, 'dashboard/admin_dashboard.html', context)




@login_required
@user_passes_test(lambda user: user.has_perm('main.view_manager_dashboard'))
def manager_dashboard(request):
    employee = Employee.objects.get(user=request.user)
    branch = employee.branch


    if branch:
        employees = Employee.objects.filter(branch=branch)
        products = Product.objects.filter(branch=branch)
        branch_employees_count = employees.count()
        branch_products_count = products.count()

        context = {
            'branch': branch,
            'employees': employees,
            'products': products,
            'branch_employees_count':branch_employees_count,
            'branch_products_count':branch_products_count,
        }

        return render(request, 'dashboard/manager_dashboard.html', context)
    else:
        # Handle the case where the user doesn't have a branch assigned
        # You might redirect to a different page or display an error message
        return render(request, 'dashboard/manager_dashboard.html', {'error_message': 'You are not assigned to a branch.'})


# salesperson_dashboard view
@login_required
@user_passes_test(lambda user: user.has_perm('main.view_cashier_dashboard'))
def cashier_dashboard(request):
    employee = Employee.objects.get(user=request.user)
    branch = employee.branch

    branch = Branch.objects.get(id=request.user.employee.branch_id)
    products = Product.objects.filter(branch=branch)
   
    today = date.today()

  

   
    context = {
        "active_icon": "dashboard",
        "products": Product.objects.filter(branch=branch).count(),
        'branch': branch,
        'products':products
    }
   


    return render( request, 'dashboard/cashier_dashboard.html',context)





