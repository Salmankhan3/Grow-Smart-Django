from django.test import TestCase,SimpleTestCase,Client
from django.urls import reverse
import json
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from home.models import Cart, CartItem, Product  
from home.views import _cart_id
from django.core.files.uploadedfile import SimpleUploadedFile

class TestViews(TestCase):

    def setUp(self):
        self.client=Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.login_url = reverse('login')  

        # Create a session cart for testing cart transfer
        session = self.client.session
        session.save()
        session_key = session.session_key
        self.image = SimpleUploadedFile(
        name='test_image.jpg',
        content=b'\x47\x49\x46\x38\x89\x61\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        content_type='image/jpeg')
        self.cart = Cart.objects.create(cart_id=session_key)
        self.product = Product.objects.create(name='Apple', price=10,desc="Fresh Apple",category='fruit',subcategory='fruit',data='2025-7-8',image=self.image)
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
    


    # # index
    def test_index_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('index'))
        print(f'Status code: {response.status_code}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
    
    def test_index_renders_for_logged_in_user(self):
        self.client.login(username='testuser', password='testpass')  
        response = self.client.get(reverse('index'))
        print(f'Status code: {response.status_code}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


    # Login View
    def test_login_successful_and_cart_assigned(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })

        # Redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

        # Ensure the cart item is now assigned to the user
        cart_item = CartItem.objects.get(id=self.cart_item.id)
        print(cart_item)


    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'Invalid username or password')

    def test_login_get_request(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    # Add to cart
    def test_add_cart_redirects_if_anonymous(self):
        response = self.client.post(reverse('add_carts', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_add_cart_creates_cart_and_cartitem_for_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')

        response = self.client.post(reverse('add_carts', args=[self.product.id]), {
        'quantity': 2
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart'))

        session_cart_id = self.client.session.session_key
        cart = Cart.objects.get(cart_id=session_cart_id)

        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.user, self.user)
