from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save




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
    def __str__(self):
        return f"Order #{self.order_id} - {self.name}"
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
# @receiver(post_save, sender=User)
# def creat_user_profile(sender,instance,created,**kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
#     else:
#         instance.profile.save()

    