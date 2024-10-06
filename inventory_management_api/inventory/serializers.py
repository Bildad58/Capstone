from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model

user = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact', 'email', 'address']

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'email', 'contact', 'address']


class InventoryProductSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    supplier_name = serializers.StringRelatedField(source='supplier', read_only=True)
    store_name = serializers.StringRelatedField(source='store', read_only=True)
    user_name = serializers.StringRelatedField(source='user', read_only=True)

    class Meta:
        model = InventoryProduct
        fields = '__all__'
class InventoryChangeSerializer(serializers.ModelSerializer):   
    class Meta:
        model = InventoryChange
        fields = ['id', 'product', 'quantity','quantity_change', 'timestamp', 'user', 'reason']
        read_only_fields = ['id', 'timestamp', 'user']
