from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters   
from rest_framework.response import Response    
from rest_framework.decorators import action
from .serializers import *
from .models import *
from .permissions import IsOwnerOrReadOnly
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from rest_framework.decorators import action
User = get_user_model()

class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
     return Supplier.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]  

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user) 
    
class InventoryProductViewSet(viewsets.ModelViewSet):
    queryset = InventoryProduct.objects.all()
    serializer_class = InventoryProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['category', 'store' 'price']
    ordering_fields = ['name', 'quantity', 'price', 'date_added']
    search_fields = ['name', 'description', 'barcode', 'supplier__name', 'store__name'] 

    def get_queryset(self):
        return InventoryProduct.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
      instance = self.get_object()
      old_quantity = instance.quantity
    
      serializer = self.get_serializer(instance, data=request.data, partial=True)
      serializer.is_valid(raise_exception=True)
        
      if getattr(instance, '_prefetched_objects_cache', None):
        instance._prefetched_objects_cache = {}

        new_quantity = serializer.validated_data.get('quantity', old_quantity)
        if new_quantity != old_quantity:
            change = new_quantity - old_quantity
            InventoryChange.objects.create(
                item=instance,
                quantity_change=change,
                user=request.user,
                reason='ADJUSTMENT'
            )

            # Check for low stock alert
            if new_quantity <= instance.reorder_level:
                self.send_low_stock_alert(instance)

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        queryset = self.get_queryset().filter(quantity__lte=F('reorder_level'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def change_history(self, request, pk=None):
        item = self.get_object()
        changes = InventoryChange.objects.filter(item=item).order_by('-timestamp')
        serializer = InventoryChangeSerializer(changes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def inventory_report(self, request):
        total_value = self.get_queryset().aggregate(
            total_value=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField()))
        )['total_value'] or 0

        low_stock_items = self.get_queryset().filter(quantity__lte=F('reorder_level')).count()

        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_changes = InventoryChange.objects.filter(
            item__in=self.get_queryset(),
            timestamp__gte=thirty_days_ago
        ).aggregate(
            sales=Sum('quantity_change', filter=models.Q(reason='SALE')),
            restocks=Sum('quantity_change', filter=models.Q(reason='RESTOCK'))
        )

        report = {
            'total_inventory_value': total_value,
            'low_stock_items_count': low_stock_items,
            'sales_last_30_days': abs(recent_changes['sales'] or 0),
            'restocks_last_30_days': recent_changes['restocks'] or 0,
        }

        return Response(report)

    def send_low_stock_alert(self, item):
        # Implement your alert logic here (e.g., send email, create notification)
        print(f"Low stock alert for {item.name} at {item.store.name}. Current quantity: {item.quantity}")


class InventoryChangeViewSet(viewsets.ModelViewSet):    
    serializer_class = InventoryChangeSerializer
    permissions_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InventoryChange.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    

    
