from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model 

User = get_user_model()
class Category(models.Model):   
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length= 150)
    contact = models.CharField(max_length= 10, unique=True, blank=False)
    email = models.EmailField(blank=False)
    address = models.TextField(blank=False)

    def __str__(self):
        return self.name
    
class Store(models.Model):  
    name = models.CharField(max_length= 150)
    address = models.TextField(blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class InventoryProduct(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])   
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]) 
    date_added = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)    
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, default=1, blank=False, null=False)  
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    reorder_level = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.name} - Quantity: {self.quantity} at {self.store.name}"

class InventoryChange(models.Model):
    product = models.ForeignKey(InventoryProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    quantity_change = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    reason = models.CharField(max_length=100, choices=[
        ('SALE', 'Sale'),
        ('RESTOCK', 'Restock'),
        ('ADJUSTMENT', 'Adjustment'),
        ('RETURN', 'Return')
    ])

    def __str__(self):
        return f"{self.product.name} - {self.quantity} at {self.timestamp}"
