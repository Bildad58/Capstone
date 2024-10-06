from rest_framework import viewsets, permissions, status, filters   
from rest_framework.response import Response    
from rest_framework.decorators import action
from .serializers import *
from .models import *
from .permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from rest_framework.decorators import action

# ViewSet for Supplier model
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Custom create method to handle supplier creation
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# ViewSet for Store model
class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Custom queryset to filter stores by the current user
    def get_queryset(self):
        user = self.request.user
        return Store.objects.filter(user=user)

# ViewSet for Category model
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]  

# ViewSet for InventoryProduct model
class InventoryProductViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryProductSerializer
    queryset = InventoryProduct.objects.all().order_by('name')
    permission_classes = [permissions.IsAuthenticated]
    # Set up filtering, ordering, and search capabilities
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['name','category', 'store', 'price']
    ordering_fields = ['name', 'quantity', 'price', 'date_added']
    search_fields = ['name', 'description',  'supplier__name', 'store__name'] 

    # Custom queryset to filter products by the current user
    def get_queryset(self):
        return InventoryProduct.objects.filter(user=self.request.user)
    
    # Add request to serializer context
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    # Custom create method to handle product creation
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Associate the created product with the current user
    def perform_create(self, serializer):
      serializer.save(user=self.request.user)

    # Custom update method to handle quantity changes and low stock alerts
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

    # Custom action to get low stock items
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        queryset = self.get_queryset().filter(quantity__lte=F('reorder_level'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Custom action to get change history for a specific item
    @action(detail=True, methods=['get'])
    def change_history(self, request, pk=None):
        item = self.get_object()
        changes = InventoryChange.objects.filter(item=item).order_by('-timestamp')
        serializer = InventoryChangeSerializer(changes, many=True)
        return Response(serializer.data)

    # Custom action to generate an inventory report
    @action(detail=False, methods=['get'])
    def inventory_report(self, request):
        # Calculate total inventory value
        total_value = self.get_queryset().aggregate(
            total_value=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField()))
        )['total_value'] or 0

        # Count low stock items
        low_stock_items = self.get_queryset().filter(quantity__lte=F('reorder_level')).count()

        # Calculate recent changes (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_changes = InventoryChange.objects.filter(
            item__in=self.get_queryset(),
            timestamp__gte=thirty_days_ago
        ).aggregate(
            sales=Sum('quantity_change', filter=models.Q(reason='SALE')),
            restocks=Sum('quantity_change', filter=models.Q(reason='RESTOCK'))
        )

        # Compile report data
        report = {
            'total_inventory_value': total_value,
            'low_stock_items_count': low_stock_items,
            'sales_last_30_days': abs(recent_changes['sales'] or 0),
            'restocks_last_30_days': recent_changes['restocks'] or 0,
        }

        return Response(report)

    # Method to send low stock alert (currently just prints to console)
    def send_low_stock_alert(self, item):
        print(f"Low stock alert for {item.name} at {item.store.name}. Current quantity: {item.quantity}")

# ViewSet for InventoryChange model
class InventoryChangeViewSet(viewsets.ModelViewSet):    
    serializer_class = InventoryChangeSerializer
    permissions_classes = [permissions.IsAuthenticated]

    # Custom queryset to filter changes by the current user
    def get_queryset(self):
        return InventoryChange.objects.filter(user=self.request.user)
    
    # Associate the created change with the current user
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)