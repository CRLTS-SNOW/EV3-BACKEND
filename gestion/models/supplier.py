# gestion/models/supplier.py
from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=150, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name