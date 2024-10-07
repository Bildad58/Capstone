from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.conf import settings 


class Category(models.Model):   
    name = models.CharField(max_length=100, unique=True, blank=False)  # Unique category name
    description = models.TextField(blank=True)  # Optional description for the category
    
    def __str__(self):
        return self.name  # String representation of the category

class Supplier(models.Model):
    name = models.CharField(max_length=150)  # Supplier's name
    contact = models.CharField(max_length=10, unique=True, blank=False)  # Unique contact number
    email = models.EmailField(blank=False)  # Supplier's email address
    address = models.TextField(blank=False)  # Supplier's physical address

    def __str__(self):
        return self.name  # String representation of the supplier

class Store(models.Model):  
    name = models.CharField(max_length=150)  # Store name
    email = models.EmailField()  # Store's email address
    address = models.TextField(blank=False)  # Store's physical address
    contact = models.CharField(max_length=10, unique=True, blank=False)  # Unique contact number

    def __str__(self):
        return self.name  # String representation of the store

class InventoryProduct(models.Model):
    name = models.CharField(max_length=100, blank=False)  # Product name
    description = models.TextField(blank=True)  # Optional product description
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, blank=False)  # Product category
    quantity = models.PositiveIntegerField(blank=False, null=False)  # Current quantity in stock
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])  # Product price
    date_added = models.DateField(auto_now_add=True)  # Date when the product was added
    last_updated = models.DateField(auto_now=True)  # Date of last update
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # User who added/manages this product
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)  # Product supplier
    store = models.ForeignKey(Store, on_delete=models.CASCADE,  blank=False, null=False)  # Store where product is located
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Optional unique barcode
    reorder_level = models.PositiveIntegerField(default=10)  # Quantity at which to reorder

    def __str__(self):
        return f"{self.name} - Quantity: {self.quantity}- @ ${self.price}"  # String representation of the product

class InventoryChange(models.Model):
    product = models.ForeignKey(InventoryProduct, on_delete=models.CASCADE)  # Associated product
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])  # New quantity after change
    quantity_change = models.PositiveIntegerField(validators=[MinValueValidator(0)])  # Amount of change
    timestamp = models.DateTimeField(auto_now=True)  # When the change occurred
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)  # User who made the change
    reason = models.CharField(max_length=100, choices=[
        ('SALE', 'Sale'),
        ('RESTOCK', 'Restock'),
        ('ADJUSTMENT', 'Adjustment'),
        ('RETURN', 'Return')
    ])  # Reason for the inventory change

    def __str__(self):
        return f"{self.product.name} - {self.quantity} at {self.timestamp}"  # String representation of the change