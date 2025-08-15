from django.test import TestCase,SimpleTestCase
from django.urls import reverse,resolve
from home.views import index,static,loginuser,regester_user,add_cart,productdisplay,tracker,cart,checkout,addproduct,productdisplay,search

# To check all view is mapped in urls.py.
class TestUrls(SimpleTestCase):
    # index
    def test_index_urls_is_resolved(self):
        url=reverse('index')
        print(url)
        self.assertEqual(resolve(url).func,index)
    #Login
    def test_login_user_urls_is_resolved(self):
        url=reverse('login')
        print(url)
        self.assertEqual(resolve(url).func,loginuser)
    # Register
    def test_register_urls_is_resolved(self):
        url=reverse('regester')
        print(url)
        self.assertEqual(resolve(url).func,regester_user)

    # Add  Cart
    def test_add_cart_urls_is_resolve(self):
        url=reverse('add_carts',kwargs={'product_id': 40})
        print(url)
        self.assertEqual(resolve(url).func,add_cart)
    # Cart
    def test_cart_urls_is_resolved(self):
        url=reverse('cart')
        print(url)
        self.assertEqual(resolve(url).func,cart)
    #check out
    
    def test_checkout_urls_is_resolved(self):
        url=reverse('checkout')
        print(url)
        self.assertEqual(resolve(url).func,checkout)

    # Add Products
    def test_add_product_urls_is_resolved(self):
        url=reverse('addproduct')
        print(url)
        self.assertEqual(resolve(url).func,addproduct)
    # Product detail
    
    def test_product_display_urls_is_resolved(self):
        url=reverse('productdisplay',kwargs={'myid': 40})
        print(url)
        self.assertEqual(resolve(url).func,productdisplay)
    # Search
    def test_search_urls_is_resolved(self):
        url=reverse('search')
        print(url)
        self.assertEqual(resolve(url).func,search)
        
    def test_tracker_urls_is_resolved(self):
        url=reverse('tracker')
        print(url)
        self.assertEqual(resolve(url).func,tracker)
        
