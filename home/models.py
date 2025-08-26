from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
import json



# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=50)
    price = models.IntegerField()
    category = models.CharField(max_length=50, default='')
    subcategory = models.CharField(max_length=50, default='')
    image = models.ImageField(upload_to='product', default='')
    data=models.DateField()
    stock = models.IntegerField(default=None, blank=True, null=True)
    owner = models.ForeignKey(User, default=None, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

#cart  model
class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True)
    date_added=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
      user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
      product=models.ForeignKey(Product, on_delete=models.CASCADE)
      cart=models.ForeignKey(Cart, on_delete=models.CASCADE,null=True)
      quantity=models.IntegerField()
      is_active=models.BooleanField(default=True)

      def __str__(self):
          return str(self.product)
      
    




class Order(models.Model):
    order_id=models.AutoField(primary_key=True)
    item_json=models.CharField(max_length=5000)
    name=models.CharField(max_length=50)
    email=models.CharField(max_length=500)
    phone=models.CharField(max_length=50)
    address=models.CharField(max_length=150)
    city=models.CharField(max_length=510)
    state=models.CharField(max_length=150)
    postal_code=models.CharField(max_length=150)
    product_owner=models.TextField(max_length=500,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True, blank=True
    )
    def __str__(self):
        return f"Order #{self.order_id} - {self.name}"




#orderitem
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="farmer_orders"
    )
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)


class OrderUpdate(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    update_id=models.AutoField(primary_key=True)
    order_id=models.IntegerField(default='')
    update_Desc=models.CharField(max_length=5000)
    timestamp=models.DateField(auto_now_add=True)
    order_status= models.CharField(max_length=10,choices=STATUS_CHOICES,default='pending',null=True,blank=True
    )
    def __str__(self):
        return self.update_Desc[0:10] + '...'
    
class Contact(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField(max_length=254)
    message=models.CharField(max_length=500)

    def __str__(self):
        return self.name


# UserProfile

class UserProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    userType=models.CharField(max_length=50,null=True,blank=True)

    def __str__(self):
        return self.user.username


# FARMER RATING
class FarmerRating(models.Model):
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings_received"
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings_given"
    )
    order_item = models.OneToOneField(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="rating"
    )
    rating = models.PositiveSmallIntegerField()  # 1–5
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'order_item')






#################### crops tracker ####################
# Farmer model
class Farmer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


# Crop model
class Crop(models.Model):
    STATUS_CHOICES = [
        ('Planning', 'Planning'),
        ('Sowing', 'Sowing'),
        ('Cultivation', 'Cultivation'),
        ('Harvest', 'Harvest'),
        ('Post-Harvest', 'Post-Harvest'),
    ]

    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name="crops")
    crop_name = models.CharField(max_length=50)
    variety = models.CharField(max_length=50, blank=True, null=True)
    season = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Planning")

    def __str__(self):
        return f"{self.crop_name} ({self.farmer.name})"


# Crop Stage model
class CropStage(models.Model):
    STAGE_CHOICES = [
        ('Planning', 'Planning'),
        ('Sowing', 'Sowing'),
        ('Cultivation', 'Cultivation'),
        ('Harvest', 'Harvest'),
        ('Post-Harvest', 'Post-Harvest'),
    ]

    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="stages")
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.crop.crop_name} - {self.stage}"


# Crop Activity model (for detailed logs under each stage)
class CropActivity(models.Model):
    stage = models.ForeignKey(CropStage, on_delete=models.CASCADE, related_name="activities")
    activity_name = models.CharField(max_length=100)
    activity_date = models.DateField()
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.activity_name} ({self.stage.stage})"