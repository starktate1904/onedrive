from django.shortcuts import redirect, render
from django.http import HttpResponse
from flask import jsonify
from products.models import  *
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json, sys
from datetime import date, datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .models import Sale, SaleItem
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def search_products_view(request):
    branch = request.user.employee.branch
    query = request.GET.get('query')
    
    if query:
        products = Product.objects.filter(
            Q(branch=branch) & 
            (
                Q(name__icontains=query) | 
                Q(description__icontains=query) 
                
            )
        )
    else:
        products = Product.objects.filter(branch=branch)
    
    return JsonResponse({"products": list(products.values())})
@require_http_methods(["GET"])
def get_product_view(request, pk):
    product = Product.objects.get(pk=pk)
    return JsonResponse({"product": product.name})

@require_http_methods(["GET"])
def sales_list_view(request):
    sales = Sale.objects.filter(employee=request.user.employee)
    return JsonResponse({"sales": list(sales.values())})

@require_http_methods(["POST"])
def sales_create_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    if 'products' not in data:
        return JsonResponse({"error": "Missing products data"}, status=400)

    products = data['products']

    if not isinstance(products, list):
        return JsonResponse({"error": "Invalid products data"}, status=400)

    employee = request.user.employee
    branch = employee.branch  # This line should be indented to the same level as the line above

    try:
        with transaction.atomic():
            sale = Sale.objects.create(employee=employee, branch=branch)
            for product_data in products:
                if not isinstance(product_data, dict):
                    raise ValueError("Invalid product data")

                if 'id' not in product_data or 'quantity' not in product_data:
                    raise ValueError("Missing product data")

                product_id = product_data['id']
                quantity_sold = product_data['quantity']

                if not isinstance(product_id, int) or not isinstance(quantity_sold, int):
                    raise ValueError("Invalid product data")

                if quantity_sold <= 0:
                    raise ValueError("Invalid quantity")

                product = Product.objects.get(id=product_id)

                if product.quantity < quantity_sold:
                    raise ValueError("Insufficient quantity")

                product.quantity -= quantity_sold
                product.save()

                SaleItem.objects.create(sale=sale, product=product, quantity=quantity_sold, price=product.price)

        return JsonResponse({"message": "Sale created successfully"})
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=400)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
@require_http_methods(["GET"])
def products_list_view(request):
    branch = request.user.employee.branch
    products = Product.objects.filter(branch=branch)
    return JsonResponse({"products": list(products.values())})

@require_http_methods(["POST"])
def add_sale(request):
    product_id = request.POST.get('product')
    quantity = request.POST.get('quantity')
    product = Product.objects.get(id=product_id)
    sale = Sale(product=product, quantity=quantity, total=product.price * int(quantity))
    sale.save()
    return JsonResponse({'message': 'Sale added successfully'})

@require_http_methods(["GET"])
def sales_detail(request, pk):
    sale = Sale.objects.get(id=pk)
    data = {'id': (sale.id), 'product': sale.product.name, 'quantity': sale.quantity, 'total': sale.total}
 
    return JsonResponse(data, safe=False)