from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import InventoryProduct, Category, Store, Supplier
from .serializers import InventoryProductSerializer

User = get_user_model()

class InventoryProductViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser',email='2Rr5T@example.com', password='testpass123')
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name='Test Category')
        self.store = Store.objects.create(name='Test Store')
        self.supplier = Supplier.objects.create(name='Test Supplier')
        
        self.product1 = InventoryProduct.objects.create(
            name='Test Product 1',
            user=self.user,
            description='Description 1',
            category=self.category,
            store=self.store,
            supplier=self.supplier,
            price=10.00,
            quantity=50,
           
        )
        self.product2 = InventoryProduct.objects.create(
            name='Test Product 2',
            user=self.user,
            description='Description 2',
            category=self.category,
            store=self.store,
            supplier=self.supplier,
            price=20.00,
            quantity=30,
           
        )
        
        self.url = reverse('inventoryproduct-list')

    def test_list_products(self):
        response = self.client.get(self.url)
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_product(self):
        data = {
            'name': 'New Product',
            'user': self.user.id,
            'description': 'New Description',
            'category': self.category.id,
            'store': self.store.id,
            'supplier': self.supplier.id,
            'price': 15.00,
            'quantity': 25,
            
        }
        response = self.client.post(self.url, data,format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InventoryProduct.objects.count(), 3)

    def test_retrieve_product(self):
        url = reverse('inventoryproduct-detail', args=[self.product1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product 1')

    def test_update_product(self):

        url = reverse('inventoryproduct-detail', args=[self.product1.id])
        data = {'name': 'Updated Product'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.name, 'Updated Product')
    def test_delete_product(self):
        url = reverse('inventoryproduct-detail', args=[self.product1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(InventoryProduct.objects.count(), 1)

    def test_filter_products(self):
        response = self.client.get(f"{self.url}?price=10.00")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Product 1')

    def test_order_products(self):
        response = self.client.get(f"{self.url}?ordering=-name")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Test Product 2')

    def test_search_products(self): 
        response = self.client.get(f"{self.url}?search=Description 2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Product 2')

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)