from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Sale, SaleItem
from products.models import Product
from branches.models import Branch
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.db import transaction
from django.db.models import F
from xhtml2pdf import pisa # type: ignore
from django.http import HttpResponse
from django.template.loader import get_template
import datetime
from datetime import date
from staff.models import *
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import SaleFilterForm




@login_required
def sale_list(request):
    active_nav_item = 'pos'
    sales = Sale.objects.filter(branch=request.user.employee.branch)
    return render(request, 'pos/sale_list.html', {'sales': sales,'active_nav_item':active_nav_item})

@login_required
def view_sale(request, sale_id):
    active_nav_item = 'pos'
    sale = Sale.objects.get(id=sale_id)
    return render(request, 'pos/view_sale.html', {'sale': sale,'active_nav_item':active_nav_item})


@login_required
def create_sale(request):
    active_nav_item = 'pos'
    today = date.today()
    employee = Employee.objects.get(user=request.user)
    products = Product.objects.filter(branch=request.user.employee.branch)
    branch = request.user.employee.branch
    if request.method == 'POST':
        # Create a new sale
        sale = Sale.objects.create(branch=request.user.employee.branch, total_amount=0, cashier_id=request.user.id)

        # Render the updated sale table and total amount as HTML
        sale_table_html = render_to_string('pos/sale_table.html', {'sale': sale})

        return JsonResponse({'sale_table': sale_table_html, 'total_amount': 0, 'sale_id': sale.id})
    else:
        products = Product.objects.filter(branch=request.user.employee.branch)
        categories = Product.objects.filter(branch=request.user.employee.branch).values('category__name').distinct()
        sale_id = request.GET.get('sale_id')

        if sale_id:
            sale_items = SaleItem.objects.filter(sale__id=sale_id)  # Get the sale items for the current sale
            sale = Sale.objects.get(id=sale_id)  # Get the current sale

            # Calculate the total for each sale item
            for item in sale_items:
                item.total = item.quantity * item.product.price
                item.save()

            # Calculate the total amount
            total_amount = sum(item.total for item in sale_items)
              # Calculate the change
            
        else:
            sale_items = []  # Initialize an empty list for sale items
            sale = Sale.objects.create(branch=request.user.employee.branch, total_amount=0, cashier_id=request.user.id)
            total_amount = 0

        return render(request, 'pos/create_sale.html', {'products': products, 'sale_items': 
                                                        sale_items,'sale':sale, 'sale_id': sale.id, 'total_amount': 
                                                        total_amount,'today':today,'employee':employee,'branch':branch, 'active_nav_item':active_nav_item,
                                                        'categories': categories})


@login_required
def search_products(request):
    active_nav_item = 'pos'
    search_term = request.GET.get('search_term', '')
    category = request.GET.get('category', '')
    branch = request.user.employee.branch
    page = request.GET.get('page', 1)

    if category:
        products = Product.objects.filter(category__name=category, branch=branch)
    else:
        products = Product.objects.filter(branch=branch)

    if search_term:
        products = products.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(make__icontains=search_term) |
            Q(model__icontains=search_term) |
            Q(price__icontains=search_term)
        )

    paginator = Paginator(products, 5)  # Show 10 products per page
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'make': product.make,
            'model': product.model,
            'quantity': product.quantity,
            'price': product.price,
            'category': product.category.name,
        })

    return JsonResponse({
        'active_nav_item':active_nav_item,
        'results': results,
        'has_previous': products.has_previous(),
        'has_next': products.has_next(),
        'previous_page_number': products.previous_page_number() if products.has_previous() else None,
        'next_page_number': products.next_page_number() if products.has_next() else None,
    }, safe=False)



@login_required
def complete_sale(request):
    today = date.today()

    if request.method == 'POST':
        sale_id = request.POST.get('sale_id')
        amount_paid = float(request.POST.get('amount_paid'))
        

        try:
            sale = Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            return JsonResponse({'error': 'Sale does not exist'})

        # Calculate the total amount of the sale
        total_amount = sale.total_amount
        total_amount = sum(item.quantity * item.price for item in SaleItem.objects.filter(sale=sale))

        # Update the product quantity
        for item in sale.saleitem_set.all():
            product = item.product
            print("Before update:", product.quantity)
            product.quantity -= item.quantity
            print("Product quantity after calculation:", product.quantity)
            product.save()
            print("After update:", product.quantity)

        # Calculate the change
        change = amount_paid - float(total_amount)

        # Create a new sale
        new_sale = Sale.objects.create(branch=request.user.employee.branch, total_amount=0, cashier_id=request.user.id)

        # Render the receipt as HTML
        receipt_html = render_to_string('pos/receipt.html', {'sale': sale, 'sale_items': sale.saleitem_set.all(), 'amount_paid': amount_paid, 'change': change,'today':today})

        return JsonResponse({'message': 'Sale completed successfully', 'change': change, 'new_sale_id': new_sale.id, 'receipt_html': receipt_html})
    else:
        return HttpResponse('Invalid request method')


@login_required
def add_product_to_sale(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))
        sale_id = request.POST.get('sale_id')

        try:
            sale = Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            return JsonResponse({'error': 'Sale does not exist'})

        product = Product.objects.get(id=product_id)

        # Check if product is already in the sale
        if SaleItem.objects.filter(sale=sale, product=product).exists():
            sale_item = SaleItem.objects.get(sale=sale, product=product)
            sale_item.quantity += quantity
            sale_item.save()
        else:
            SaleItem.objects.create(sale=sale, product =product, quantity=quantity, price=product.price)

        # Recalculate the total amount
        sale.total_amount = sum(item.quantity * item.price for item in SaleItem.objects.filter(sale=sale))
        sale.save()

        # Render the updated sale table and total amount as HTML
        sale_items = SaleItem.objects.filter (sale=sale)
        sale_table_html = render_to_string('pos/sale_table.html', {'sale': sale, 'sale_items': sale_items})

        return JsonResponse({'sale_table': sale_table_html, 'total_amount': sale.total_amount})
    else:
        return HttpResponse('Invalid request method')



@login_required
def remove_product_from_sale(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        sale_id = request.POST.get('sale_id')

        try:
            sale = Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            return JsonResponse({'error': 'Sale does not exist'})

        product = Product.objects.get(id=product_id)

        # Check if product is in the sale
        if SaleItem.objects.filter(sale=sale, product=product).exists():
            sale_item = SaleItem.objects.get(sale=sale, product=product)
            sale_item.delete()

            # Recalculate the total amount
            sale.total_amount = sum(item.quantity * item.price for item in SaleItem.objects.filter(sale=sale))
            sale.save()

            # Render the updated sale table and total amount as HTML
            sale_items = SaleItem.objects.filter(sale=sale)
            sale_table_html = render_to_string('pos/sale_table.html', {'sale': sale, 'sale_items': sale_items})

            return JsonResponse({'sale_table': sale_table_html, 'total_amount': sale.total_amount})
        else:
            return JsonResponse({'error': 'Product is not in the sale'})
    else:
        return HttpResponse('Invalid request method')
  

       

@login_required
def sales_list_view(request):

    active_nav_item = 'sales'
    sales = Sale.objects.all()

    # Search feature
    search_query = request.GET.get('search')
    if search_query:
        sales = sales.filter(product__name__icontains=search_query)

    # Filtering by date
    date_filter = request.GET.get('date_filter')
    if date_filter == 'today':
        sales = sales.filter(date_created=request.date.today())
    elif date_filter == 'yesterday':
        sales = sales.filter(date_created=request.date.today() - datetime.timedelta(days=1))
    elif date_filter == 'this_week':
        sales = sales.filter(date_created__gte=request.date.today() - datetime.timedelta(days=7))
    elif date_filter == 'last_week':
        sales = sales.filter(date_created__gte=request.date.today() - datetime.timedelta(days=14), date_created__date__lt=request.date.today() - datetime.timedelta(days=7))

    # Filtering by money
    money_filter = request.GET.get('money_filter')
    if money_filter == 'high_to_low':

        sales = sales.order_by('-total_amount')
    elif money_filter == 'low_to_high':

        sales = sales.order_by('total_amount')

    # Pagination
    paginator = Paginator(sales, 10)
    page_number = request.GET.get('page')
    sales_page = paginator.get_page(page_number)

    # Filter form
    filter_form = SaleFilterForm(request.GET)

    return render(request, 'reports/sales.html', {
        'sales': sales_page,
        'active_nav_item': active_nav_item,
        'filter_form': filter_form,
        'search_query': search_query,
        'date_filter': date_filter,
        'money_filter': money_filter,
    })
   


