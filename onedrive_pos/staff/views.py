from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .models import *
from branches.models import Branch
from auth_pos.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import User
from django.contrib.auth.hashers import make_password

User = get_user_model()





#  employee management CRUD views
@login_required
@user_passes_test(lambda user: user.has_perm('main.view_employee_list'))
@user_passes_test(lambda user: user.has_perm('main.view_branch_list'))
def employee_list(request):
    active_nav_item = 'staff'
    try:
        employees = Employee.objects.all()
        branches = Branch.objects.all()
        users = User.objects.all()

        context = {
            'active_nav_item':active_nav_item,
            'employees': employees,
            'branches': branches,
            'users': users,
        }
        return render(request, 'staff/employees.html', context)
    except Exception as e:
        messages.error(request, 'Error loading employee list: {}'.format(e))
        return redirect('staffs:employee_list')


@login_required
@user_passes_test(lambda user: user.has_perm('main.add_employee'))
@user_passes_test(lambda user: user.has_perm('main.view_branch_list'))
def employee_create(request):
    active_nav_item = 'staff'
    if request.method == 'POST':

        try:
            branch_id = request.POST.get('branch')
            username = request.POST.get('username')
            email = request.POST.get('email')
            role = request.POST.get('role')
            password = request.POST.get('password')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email address already in use')
                return redirect('staffs:employee_create')

            user = User.objects.create_user(username=username, email=email)
            user.role = role
            user.set_password(password)  # Set the password using set_password
            user.save()
            branch = Branch.objects.get(pk=branch_id)
            Employee.objects.create(user=user, branch=branch)
            messages.success(request, 'Employee created successfully!')
            return redirect('staffs:employee_list')
        except Branch.DoesNotExist:
            messages.error(request, 'Invalid branch selected.')
        except Exception as e:
            messages.error(request, 'Error creating employee: {}'.format(e))
    branches = Branch.objects.all()
    users = User.objects.all()  # Consider filtering users if needed
    return render(request, 'staff/employees.html', {'branches': branches, 'users': users,'active_nav_item':active_nav_item})


@login_required
@user_passes_test(lambda user: user.has_perm('main.update_employee'))
@user_passes_test(lambda user: user.has_perm('main.view_branch_list'))
def employee_update(request, employee_id):
    active_nav_item = 'staff'
    try:
        employee = Employee.objects.get(pk=employee_id)
        if request.method == 'POST':
            email = request.POST.get('email')
            branch_id = request.POST.get('branch')
            role = request.POST.get('role')
            password = request.POST.get('password')

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
            return render(request, 'staff/employees.html', {'employee': employee, 'branches': branches,'active_nav_item':active_nav_item})
    except Employee.DoesNotExist:
        messages.error(request, 'Employee not found.')
    except Exception as e:
        messages.error(request, 'Error updating employee: {}'.format(e))
    return redirect('staffs:employee_list')


@login_required
@user_passes_test(lambda user: user.has_perm('main.delete_employee'))
@user_passes_test(lambda user: user.has_perm('main.view_branch_list'))
def employee_delete(request, employee_id):
    active_nav_item = 'staff'
    try:
        employee = Employee.objects.get(pk=employee_id)
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
    except Employee.DoesNotExist:
        messages.error(request, 'Employee not found.')
    except Exception as e:
        messages.error(request, 'Error deleting employee: {}'.format(e))
    return redirect('staffs:employee_list',{'active_nav_item':active_nav_item})