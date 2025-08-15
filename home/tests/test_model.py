from django.test import TestCase,SimpleTestCase,Client
from django.urls import reverse
import json
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from home.models import Cart, CartItem, Product  
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date


class TestModels(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Test Product',
            desc='Test Description',
            price=100,
            category='Test Category',
            subcategory='Test Subcategory',
            image=SimpleUploadedFile(
                name='test.jpg',
                content=b'\x47\x49\x46\x38\x89\x61\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                content_type='image/jpeg'
            ),
            data=date(2025, 8, 1)
        )
        print(self.product.image.name)
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.desc, 'Test Description')
        self.assertEqual(self.product.price, 100)
        self.assertEqual(self.product.category, 'Test Category')
        self.assertEqual(self.product.subcategory, 'Test Subcategory')
        self.assertTrue(self.product.image.name.startswith('product/test'))
        self.assertEqual(self.product.data, date(2025, 8, 1))

    def test_product_str_method(self):
        self.assertEqual(str(self.product), 'Test Product')
 
