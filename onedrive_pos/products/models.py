import django
from django.db import models
from django.contrib.auth.models import AbstractUser
import django.utils.timezone
from branches.models import Branch
from django.forms import model_to_dict



#  carPart model
class Product(models.Model):
    name = models.CharField(max_length=100)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    description = models.TextField(max_length=255,)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    def to_json(self):
        item = model_to_dict(self)
        item['id'] = self.id
        item['text'] = self.name
        item['text'] = self.make
        item['text'] = self.model
        item['text'] = self.description
        item['branch'] = self.branch.name
        item['quantity'] = 1
        item['total_product'] = 0
        return item
