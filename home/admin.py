from django.contrib import admin
from home.models import Product
from home.models import Order,OrderUpdate,Cart,CartItem,Contact,UserProfile
from home.models import FarmerRating,Notification,FarmerProfile,CropPlan
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderUpdate)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Contact)
admin.site.register(UserProfile)
admin.site.register(FarmerRating)
admin.site.register(Notification)
admin.site.register(FarmerProfile)
admin.site.register(CropPlan)
