# Import necessary modules and classes from Django REST framework and other libraries
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

# ViewSet for Supplier model
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()  # Get all suppliers from the database
    serializer_class = SupplierSerializer  # Serializer for supplier data
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

    # Custom create method to handle supplier creation
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  # Get and validate the data
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # Create the supplier instance
        headers = self.get_success_headers(serializer.data)  # Get success headers
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)  # Return response with created supplier data

# ViewSet for Store model
class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer  # Serializer for store data
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

    # Custom queryset to filter stores by the current user
    def get_queryset(self):
        user = self.request.user  # Get the current user
        return Store.objects.filter(user=user)  # Filter stores owned by the current user

# ViewSet for Category model
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()  # Get all categories from the database
    serializer_class = CategorySerializer  # Serializer for category data
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

# ViewSet for InventoryProduct model
class InventoryProductViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryProductSerializer  # Serializer for inventory product data
    queryset = InventoryProduct.objects.all().order_by('id')  # Get all products ordered by name
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view
    
    # Set up filtering, ordering, and search capabilities
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['name', 'category', 'store', 'price']  # Fields to filter by
    ordering_fields = ['name', 'quantity', 'price', 'date_added']  # Fields to order by
    search_fields = ['name', 'description', 'supplier__name', 'store__name']  # Fields to search in

    # Custom queryset to filter products by the current user
    def get_queryset(self):
        return InventoryProduct.objects.filter(user=self.request.user)  # Filter products owned by the current user

    # Add request to serializer context
    def get_serializer_context(self):
        context = super().get_serializer_context()  # Get the default context
        context.update({"request": self.request})  # Add the request to the context
        return context

    # Custom create method to handle product creation
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  # Get and validate the data
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # Create the product instance
        serializer.save()  # Save the new product
        headers = self.get_success_headers(serializer.data)  # Get success headers
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)  # Return response with created product data

    # Associate the created product with the current user
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Save the product with the current user as the owner

    # Custom update method to handle quantity changes and low stock alerts
    def update(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the current product instance
        old_quantity = instance.quantity  # Store the old quantity
        serializer = self.get_serializer(instance, data=request.data, partial=True)  # Get and validate the data
        serializer.is_valid(raise_exception=True)
        
        # Clear pre-fetched objects cache for accurate updates
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        new_quantity = serializer.validated_data.get('quantity', old_quantity)  # Get the new quantity
        if new_quantity != old_quantity:  # Check if the quantity has changed
            change = new_quantity - old_quantity  # Calculate the change
            InventoryChange.objects.create(  # Record the change
                item=instance,
                quantity_change=change,
                user=request.user,  # Associate with the current user
                reason='ADJUSTMENT'
            )

            # Check for low stock alert
            if new_quantity <= instance.reorder_level:
                self.send_low_stock_alert(instance)  # Send alert if low stock

        return Response(serializer.data)  # Return response with updated product data

    # Custom action to get low stock items
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        queryset = self.get_queryset().filter(quantity__lte=F('reorder_level'))  # Get low stock products
        serializer = self.get_serializer(queryset, many=True)  # Serialize the low stock products
        return Response(serializer.data)  # Return response with low stock products data

    # Custom action to get change history for a specific item
    @action(detail=True, methods=['get'])
    def change_history(self, request, pk=None):
        item = self.get_object()  # Get the current product instance
        changes = InventoryChange.objects.filter(item=item).order_by('-timestamp')  # Get change history for the item
        serializer = InventoryChangeSerializer(changes, many=True)  # Serialize the change history
        return Response(serializer.data)  # Return response with change history data

    # Custom action to generate an inventory report
    @action(detail=False, methods=['get'])
    def inventory_report(self, request):
        # Calculate total inventory value
        total_value = self.get_queryset().aggregate(
            total_value=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField()))
        )['total_value'] or 0  # Total inventory value

        # Count low stock items
        low_stock_items = self.get_queryset().filter(quantity__lte=F('reorder_level')).count()  # Count low stock products

        # Calculate recent changes (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)  # Date 30 days ago
        recent_changes = InventoryChange.objects.filter(
            item__in=self.get_queryset(),
            timestamp__gte=thirty_days_ago
        ).aggregate(
            sales=Sum('quantity_change', filter=models.Q(reason='SALE')),  # Total sales in the last 30 days
            restocks=Sum('quantity_change', filter=models.Q(reason='RESTOCK'))  # Total restocks in the last 30 days
        )

        # Compile report data
        report = {
            'total_inventory_value': total_value,
            'low_stock_items_count': low_stock_items,
            'sales_last_30_days': abs(recent_changes['sales'] or 0),
            'restocks_last_30_days': recent_changes['restocks'] or 0,
        }

        return Response(report)  # Return response with the inventory report

    # Method to send low stock alert (currently just prints to console)
    def send_low_stock_alert(self, item):
        print(f"Low stock alert for {item.name} at {item.store.name}. Current quantity: {item.quantity}")

# ViewSet for InventoryChange model
class InventoryChangeViewSet(viewsets.ModelViewSet):    
    serializer_class = InventoryChangeSerializer  # Serializer for inventory change data
    permissions_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

    # Custom queryset to filter changes by the current user
    def get_queryset(self):
        return InventoryChange.objects.filter(user=self.request.user)  # Filter changes by the current user
    
    # Associate the created change with the current user
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Save the change with the current user as the owner
