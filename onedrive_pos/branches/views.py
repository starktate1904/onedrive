from django.shortcuts import render
import django
from django.shortcuts  import render 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .models import *
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from products.models import Product # type: ignore












# Branch management  CRUD views
@login_required
@user_passes_test(lambda user: user.has_perm('main.view_branch_list'))
def branch_list(request):
    branches = Branch.objects.all()
    return render(request, 'branches/branches.html', {'branches': branches})


@login_required
@user_passes_test(lambda user: user.has_perm('main.add_branch'))
def branch_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')

        # Validate input
        if not location or not name :
            messages.error(request, 'Please fill in all fields')
            return render(request, 'branches/branches.html')

        Branch.objects.create(name=name, location=location)
        messages.success(request, 'Branch created successfully!')
        return redirect('branches:branch_list')  # Redirect to branch list after success
      
    return render(request, 'branches/branches.html', )


@login_required
@user_passes_test(lambda user: user.has_perm('main.update_branch'))
def branch_update(request ):
    branch = Branch.objects.get()
    context ={'branch':branch,}
    return render(request, 'branches/branches.html', context)


@login_required
@user_passes_test(lambda user: user.has_perm('main.update_branch'))
def save_update_branch(request):
    if request.method == 'POST':
        branches = Branch.objects.all()
        branchid = request.POST.get('id')
        branch =Branch.objects.get(id=branchid)
        branch.name = request.POST.get('name')
        branch.location = request.POST.get('location')
       
        branch.save()
        context = {
        'branches': branches,
    }
  
    return render (request, 'branches/branches.html', context)


@login_required
@user_passes_test(lambda user: user.has_perm('main.delete_branch'))
def branch_delete(request, id):
    branches = Branch.objects.all()
    branch = Branch.objects.get(id=id)
    branch.delete()
    
    context = {
        'branch': branch,
        'branches':branches
    }
    messages.success(request, 'branch deleted successfully!')


    return render(request ,'branches/branches.html', context)




@login_required
@user_passes_test(lambda user: user.has_perm('main.view_branch_list'))
def branch_detail(request, branch_id):
    branch = Branch.objects.get( pk=branch_id)
    return render(request,'branches/branches.html', {'branch': branch})




@login_required
@user_passes_test(lambda user: user.has_perm('main.view_branch_list'))
def branch_products(request, branch_id):
    branch = Branch.objects.get(id=branch_id)
    products = branch.product_set.select_related('branch')  # Optimize query
    branch_products_count = products.count()

    # Get the search query from the GET parameters
    search_query = request.GET.get('search', '')

    # Filter products based on the search query
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) 
 |
            Q(make__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(price__icontains=search_query)
        )

   

    # Paginate the filtered and ordered products
    page_size = 10
    paginator = Paginator(products.order_by('name'), page_size)

    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages) 
  # If page is out of range

    

    context = {
        'branch': branch,
        'products': products,
        'paginator': paginator,
        'search_query': search_query,
        'branch_options': Branch.objects.all(),  # Pass branch options for transfer form
        'branch_products_count':branch_products_count,
    }

    return render(request, 'branches/branch_products.html', context)
    
