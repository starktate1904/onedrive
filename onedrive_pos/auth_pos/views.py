from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .models import *
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, F, FloatField
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncMonth
from datetime import datetime, date
import json
from django.core.serializers.json import DjangoJSONEncoder
import datetime
from products.models import *
from staff.models import *
from .models import User
from django.contrib.auth import get_user_model
from datetime import date
from django.contrib.auth.decorators import login_required
from pos.models import Sale
from django.db.models import Sum
from django.db.models.functions import Trunc
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
import json
from django.db.models import F
from django.urls import reverse
from user_profile.models import *

User = get_user_model()



def loader_view(request):
    return render(request, 'scripts/loader.html')


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



# login view
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
       
        user = authenticate(request,username=username,password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Login successful!')

            # Set a session variable to store the redirect URL
            if user.role == 'admin':
                request.session['redirect_url'] = 'auth_pos:admin_dashboard'
            elif user.role == 'manager':
                request.session['redirect_url'] = 'auth_pos:manager_dashboard'
            else:
                request.session['redirect_url'] = 'auth_pos:cashier_dashboard'

            # Reverse the URL
            redirect_url = reverse(request.session['redirect_url'])

            # Display the loader
            return render(request, 'scripts/loader.html', {'redirect_url': redirect_url})
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'authentication/login.html')
    else:
        return render(request, 'authentication/login.html')



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
    today = date.today()

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

    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    # Calculate the total revenue
    total_revenue = Sale.objects.aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0

    # Count the number of sales
    total_sales = Sale.objects.count()

    # Get the top products
    top_products = Product.objects.annotate(total_sales=Sum('sale_items__quantity') * F('sale_items__price')).order_by('-total_sales')[:3]

    # Get the month earnings
    month_earnings = Sale.objects.annotate(month=TruncMonth('date_created')).values('month').annotate(earnings=Sum('total_amount')).order_by('month')

    # Create lists for the top products names and quantities
    top_products_names = [product.name for product in top_products]
    top_products_quantity = [product.total_sales for product in top_products]

    # Create lists for the month earnings
    month_earnings_labels = [month['month'].strftime('%b') for month in month_earnings]
    month_earnings_data = [float(month['earnings']) for month in month_earnings]

    # Calculate earnings per month
    today = date.today()
    year = today.year
    monthly_earnings = []
    for month in range(1, 13):
        earning = Sale.objects.filter(date_created__year=year, date_created__month=month).aggregate(
            total_variable=Coalesce(Sum(F('total_amount')), 0.0, output_field=FloatField())).get('total_variable')
        monthly_earnings.append(earning)

    # Calculate annual earnings
    annual_earnings = Sale.objects.filter(date_created__year=year).aggregate(total_variable=Coalesce(
        Sum(F('total_amount')), 0.0, output_field=FloatField())).get('total_variable')
    annual_earnings = format(annual_earnings, '.2f')

    # AVG per month
    avg_month = format(sum(monthly_earnings)/12, '.2f')

    # Convert the lists to JSON strings
    import json
    
    month_earnings_labels = json.dumps(month_earnings_labels)
    month_earnings_data = json.dumps(month_earnings_data)
    monthly_earnings = json.dumps(monthly_earnings)

    context = {
        'today':today,
        'user_profile':user_profile,
        'products_count': products_count,
        'branches_count': branches_count,
        'employee_count': employee_count,
        'greeting': greeting,
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'top_products': top_products,
        'top_products_names': top_products_names,
        'month_earnings_labels': json.dumps(month_earnings_labels),
        'month_earnings_data': json.dumps(month_earnings_data),
        'top_products_quantity': top_products_quantity,
        'monthly_earnings': monthly_earnings,
        'annual_earnings': annual_earnings,
        'avg_month': avg_month,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


    # 




# branch manager_dashboard view
@login_required
@user_passes_test(lambda user: user.has_perm('main.view_manager_dashboard'))
def manager_dashboard(request):
    employee = Employee.objects.get(user=request.user)
    branch = employee.branch
    today = date.today()
    current_time = datetime.datetime.now()

    # Determine the greeting based on the time of day
    if current_time.hour < 12:
        greeting = "Good Morning"
    elif current_time.hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None

    if branch:
        employees = Employee.objects.filter(branch=branch)
        products = Product.objects.filter(branch=branch)
        branch_employees_count = employees.count()
        branch_products_count = products.count()

        # Calculate total sales for the branch
        total_sales = Sale.objects.filter(branch=branch).count()

        # Calculate total revenue for the branch
        total_revenue = Sale.objects.filter(branch=branch).aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0

        # Get top products for the branch
        top_products = Product.objects.filter(branch=branch).annotate(total_sales=Sum('sale_items__quantity') * F('sale_items__price')).order_by('-total_sales')[:3]

        # Get top products names and quantities
        top_products_names = [product.name for product in top_products]
        top_products_quantity = [product.total_sales for product in top_products]

        # Calculate earnings per month for the branch
        monthly_earnings = []
        for month in range(1, 13):
            earning = Sale.objects.filter(branch=branch, date_created__year=today.year, date_created__month=month).aggregate(
                total_variable=Coalesce(Sum(F('total_amount')), 0.0, output_field=FloatField())).get('total_variable')
            monthly_earnings.append(earning)

        # Calculate annual earnings for the branch
        annual_earnings = Sale.objects.filter(branch=branch, date_created__year=today.year).aggregate(total_variable=Coalesce(
            Sum(F('total_amount')), 0.0, output_field=FloatField())).get('total_variable')
        annual_earnings = format(annual_earnings, '.2f')

        # AVG per month
        avg_month = format(sum(monthly_earnings)/12, '.2f')

        context = {
            'greeting':greeting,
            'today':today,
            'branch': branch,
            'employees': employees,
            'products': products,
            'branch_employees_count':branch_employees_count,
            'branch_products_count':branch_products_count,
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'top_products': top_products,
            'top_products_names': top_products_names,
            'top_products_quantity': top_products_quantity,
            'monthly_earnings': monthly_earnings,
            'annual_earnings': annual_earnings,
            'avg_month': avg_month,
            'user_profile': user_profile,
        }

        return render(request, 'dashboard/manager_dashboard.html', context)
    else:
        # Handle the case where the user doesn't have a branch assigned
        # You might redirect to a different page or display an error message
        return render(request, 'dashboard/manager_dashboard.html', {'error_message': 'You are not assigned to a branch.'})



# cashier_dashboard view
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





