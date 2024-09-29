from django.shortcuts import render,redirect
from staff.models import Employee
from auth_pos.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import *
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages



@login_required
def profile_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    context = {'user':user }
    return render(request, 'profile/profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password: 
            user = request.user
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!') 

            return redirect('profile:profile_detail',pk=request.user.pk)
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'profile/profile.html')




@login_required
def update_user_details(request):
    if request.method == 'POST':
        username =  request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email') 

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save() 

        messages.success(request, 'User details updated successfully!')
        return redirect('profile:profile_detail', pk=request.user.pk)
    return render(request, 'profile/profile.html')