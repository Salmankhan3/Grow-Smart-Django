from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
import json
from home.geocode import geocode_location



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
        return f"{self.user.username} - {self.userType}"


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




class Notification(models.Model):
    exporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.exporter.username}: {self.message[:30]}"

#################### crops tracker ####################
class FarmerProfile(models.Model):
    farmer = models.OneToOneField(User, on_delete=models.CASCADE)
    land_size = models.CharField(max_length=50,null=True)
    location=models.CharField(max_length=100,null=True,blank=True)
    Agroecological_zone=models.CharField(max_length=100,null=True,blank=True)
    soil_type = models.CharField(max_length=50)
    water_source = models.CharField(
        max_length=20,
        choices=[("tube_well", "Tube well"), ("canal", "Canal"), ("rain", "Rain")],
        default="tube_well"
    )
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-geocode if location is set but lat/lon missing
        if self.location and (not self.lat or not self.lon):
            lat, lon = geocode_location(self.location)
            if lat and lon:
                self.lat = lat
                self.lon = lon
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.farmer.username}'s Profile"
class CropPlan(models.Model):
    STAGES = [
        (1, "Crop Selection"),
        (2, "Soil Preparation"),
        (3, "Seed Growing"),
        (4, "Irrigation & Fertilisation"),
        (5, "Pest & Disease Control"),
        (6, "Harvesting"),
        (7, "Post-Harvesting"),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, null=True, blank=True)

    crop_name = models.CharField(max_length=100, blank=True, null=True)
    crop_variety=models.CharField(max_length=50,blank=True,null=True)
    current_stage = models.IntegerField(choices=STAGES, default=1)
    created_at = models.DateField(auto_now_add=True, blank=True, null=True)
    harvesting_date=models.DateField(auto_now=False, auto_now_add=False,blank=True,null=True)
    last_ai_advice = models.TextField(blank=True, null=True)
    crop_field=models.IntegerField(blank=True,null=True)

    def stage_label(self):
        return dict(self.STAGES).get(self.current_stage, "Unknown")

    def next_stage(self):
        if self.current_stage < 7:
            self.current_stage += 1
            self.save()
