from django.contrib import admin
from .models import InventoryProduct, InventoryChange  

admin.site.register(InventoryProduct)  
admin.site.register(InventoryChange)     
# Register your models here.
