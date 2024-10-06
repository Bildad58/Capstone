from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# router = DefaultRouter()
# router.register(r'categories', CategoryViewSet, basename='category')
# router.register(r'products', InventoryProductViewSet, basename='inventoryproduct')
# router.register(r'changes', InventoryChangeViewSet, basename='inventorychange')
# router.register(r'suppliers', SupplierViewSet, basename='supplier')
# router.register(r'stores', StoreViewSet, basename='store')


# urlpatterns = [
#     path('', include(router.urls)),
    


urlpatterns = [
    # Category URLs
    path('categories/', CategoryViewSet.as_view({'get': 'list', 'post': 'create', 'put': 'update'}), name='category-list'),
    path('categories/<int:pk>/', CategoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='category-detail'),

    # InventoryProduct URLs
    path('products/', InventoryProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='inventoryproduct-list'),
    path('products/<int:pk>/', InventoryProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='inventoryproduct-detail'),

    # InventoryChange URLs
    path('changes/', InventoryChangeViewSet.as_view({'get': 'list', 'post': 'create'}), name='inventorychange-list'),
    path('changes/<int:pk>/', InventoryChangeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='inventorychange-detail'),

    # Supplier URLs
    path('suppliers/', SupplierViewSet.as_view({'get': 'list', 'post': 'create'}), name='supplier-list'),
    path('suppliers/<int:pk>/', SupplierViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='supplier-detail'),

    # Store URLs
    path('stores/', StoreViewSet.as_view({'get': 'list', 'post': 'create'}), name='store-list'),
    path('stores/<int:pk>/', StoreViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='store-detail'),
]
