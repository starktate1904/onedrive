from django.db import models
from django.contrib.auth.models import AbstractUser


# user model 
class User(AbstractUser):
    email = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    ROLE_CHOICES = (
        ('admin', 'Admin'), 
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')

    def __str__(self):
        return self.username



