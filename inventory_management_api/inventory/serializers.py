from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryProduct
        fields = ['id', 'name']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact', 'email', 'address']

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address']

from decimal import Decimal

class InventoryProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), allow_null=True)
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.00')  # Use a Decimal instance
    )

    class Meta:
        model = InventoryProduct
        fields = ['id', 'name', 'description', 'category', 'quantity', 'price', 'date_added', 'last_updated', 'supplier', 'store', 'barcode', 'reorder_level']
        read_only_fields = ['id','date_added', 'last_updated', 'reorder_level']

    
   

    def create(self, validated_data):
        user = self.context['request'].user
        return InventoryProduct.objects.create(user=user, **validated_data)
    
class InventoryChangeSerializer(serializers.ModelSerializer):   
    class Meta:
        model = InventoryChange
        fields = ['id', 'product', 'quantity', 'timestamp', 'user', 'reason']
        read_only_fields = ['id', 'timestamp', 'user']
