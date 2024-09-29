from django.db import models
from branches.models import Branch
from products.models import Product
from staff.models import Employee
from django.utils import timezone





class Sale(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

