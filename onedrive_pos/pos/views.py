from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Sale, SaleItem
from products.models import Product
from branches.models import Branch
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.db import transaction
from django.db.models import F
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import get_template
import datetime
from datetime import date



@login_required
def sale_list(request):
    sales = Sale.objects.filter(branch=request.user.employee.branch)
    return render(request, 'pos/sale_list.html', {'sales': sales})

@login_required
def view_sale(request, sale_id):
    sale = Sale.objects.get(id=sale_id)
    return render(request, 'pos/view_sale.html', {'sale': sale})

@login_required
def create_sale(request):
    if request.method == 'POST':
        # Create a new sale
        sale = Sale.objects.create(branch=request.user.employee.branch, total_amount=0, cashier_id=request.user.id)

        # Render the updated sale table and total amount as HTML
        sale_table_html = render_to_string('pos/sale_table.html', {'sale': sale})

        return JsonResponse({'sale_table': sale_table_html, 'total_amount': 0, 'sale_id': sale.id})
    else:
        products = Product.objects.filter(branch=request.user.employee.branch)
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
        else:
            sale_items = []  # Initialize an empty list for sale items
            sale = Sale.objects.create(branch=request.user.employee.branch, total_amount=0, cashier_id=request.user.id)
            total_amount = 0

        return render(request, 'pos/create_sale.html', {'products': products, 'sale_items': sale_items,'sale':sale, 'sale_id': sale.id, 'total_amount': total_amount})

@login_required
def search_products(request):
    search_term = request.GET.get('search_term', '')
    branch = request.user.employee.branch
    products = Product.objects.filter(name__icontains=search_term)
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
        })
    return JsonResponse(results, safe=False)

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

        # Update the product quantity
        for item in sale.saleitem_set.all():
            product = item.product
            print("Before update:", product.quantity)
            product.quantity -= item.quantity
            print("Product quantity after calculation:", product.quantity)
            product.save()
            print("After update:", product.quantity)

        # Calculate the change
        change = amount_paid - float(sale.total_amount)

        # Create a new sale
        new_sale = Sale.objects.create(branch=request.user.employee.branch, total_amount=0, cashier_id=request.user.id)

        # Render the receipt as HTML
        sale_items = SaleItem.objects.filter(sale=sale)
        receipt_html = render_to_string('pos/receipt.html', {'sale': sale, 'sale_items': sale_items, 'amount_paid': amount_paid, 'change': change,'today':today})

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
  

       