from django.shortcuts import render
import django
from django.shortcuts  import render 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .models import *
from branches.models import Branch
from auth_pos.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import datetime
from django.db.models import Sum
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import get_user_model
from .models import User

User = get_user_model()





#  employee management CRUD views
@login_required
@user_passes_test(lambda user: user.has_perm('main.view_employee_list'))
@user_passes_test(lambda user: user.has_perm('main.view_branch_list'))
def employee_list(request):
    employees = Employee.objects.all()
    branches = Branch.objects.all()
    users = User.objects.all()

    context = {
        'employees': employees,
        'branches': branches,
        'users': users,
    }
    
    
    return render(request, 'staff/employees.html', context)


@login_required
@user_passes_test(lambda user: user.has_perm('main.add_employee'))
@user_passes_test(lambda user: user.has_perm('main.view_branch_list'))
def employee_create(request):
    if request.method == 'POST':
        branch_id = request.POST.get('branch')
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')

        if User.objects.filter(email=email).exists():
            raise ValidationError('Email address already in use')

        try:
            user = User.objects.create_user(username=username, password=request.POST.get('password'), email=email)
            user.role = role
            user.save()
            branch = Branch.objects.get(pk=branch_id)
            Employee.objects.create(user=user, branch=branch)
            messages.success(request, 'Employee created successfully!')
            return redirect('staffs:employee_list')
        except Branch.DoesNotExist:
            messages.error(request, 'Invalid branch selected.')

    branches = Branch.objects.all()
    users = User.objects.all()  # Consider filtering users if needed
    return render(request, 'staff/employees.html', {'branches': branches, 'users': users})


@login_required
@user_passes_test(lambda user: user.has_perm('main.update_employee'))
@user_passes_test(lambda user: user.has_perm('main.view_branch_list'))
def employee_update(request, employee_id):
    employee = Employee.objects.get(pk=employee_id)
    if request.method == 'POST':
        email = request.POST.get('email')
        branch_id = request.POST.get('branch')
        role = request.POST.get('role')
        password = request.POST.get('password')
         # Get the role from the form

        try:
            branch = Branch.objects.get(pk=branch_id)
            employee.branch = branch
            employee.user.username = request.POST.get('username')
            employee.user.role = role  # Update the user's role
            employee.user.email = email  # Update the user's email  
            employee.user.set_password(password)  # Update the user's password
            employee.user.save()
            employee.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('staffs:employee_list')
        except Branch.DoesNotExist:
            messages.error(request, 'Invalid branch selected.')
    else:
        branches = Branch.objects.all()
        return render(request, 'staff/employees.html', {'employee': employee, 'branches': branches})



@login_required
@user_passes_test(lambda user: user.has_perm('main.delete_employee'))
@user_passes_test(lambda user: user.has_perm('main.view_branch_list'))
def employee_delete(request, employee_id):
    employee = Employee.objects.get(pk=employee_id)
    employee.delete()
    messages.success(request, 'Employee deleted successfully!')
    return redirect('staffs:employee_list')


