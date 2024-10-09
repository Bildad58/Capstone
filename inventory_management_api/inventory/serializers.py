from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model

user = get_user_model()

# Serializer for Category model
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']  # Fields to be included in the serialized output

    # Method to save the user when creating a new category
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 

# Serializer for Supplier model
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact', 'email', 'address']  # Fields to be included in the serialized output

# Serializer for Store model
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'email', 'contact', 'address']  # Fields to be included in the serialized output

# Serializer for InventoryProduct model
class InventoryProductSerializer(serializers.ModelSerializer):
    # Read-only fields to display related model names
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    supplier_name = serializers.StringRelatedField(source='supplier', read_only=True)
    store_name = serializers.StringRelatedField(source='store', read_only=True)
    user_name = serializers.StringRelatedField(source='user', read_only=True)

    class Meta:
        model = InventoryProduct
        fields = '__all__'  # Include all fields from the InventoryProduct model

# Serializer for InventoryChange model
class InventoryChangeSerializer(serializers.ModelSerializer):   
    class Meta:
        model = InventoryChange
        fields = ['id', 'product', 'quantity', 'quantity_change', 'timestamp', 'user', 'reason']  # Fields to be included in the serialized output
        read_only_fields = ['id', 'timestamp', 'user']  # Mark these fields as read-only
