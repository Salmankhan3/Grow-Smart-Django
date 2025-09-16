from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json
from datetime import date
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from home.models import Product
from home.models import Order
from home.models import OrderUpdate,Cart,CartItem,Contact,UserProfile
from home.models import OrderItem,FarmerRating,Notification,CropPlan,FarmerProfile,CropOutcome
from django.db.models import Q
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
import re
from decimal import Decimal
from django.db.models import Avg, Count
from home.weather import get_weather
import requests
from home.rag_client import query_rag,RAGError
from .forms import CropOutcomeForm

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

def index(request):
    if request.user.is_anonymous:
        return redirect('login')
    products = Product.objects.select_related('owner').annotate(
        avg_rating=Avg('owner__ratings_received__rating'),
        total_reviews=Count('owner__ratings_received')
    )
    unread_count = 0
    recent_notifications = []

    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            exporter=request.user, is_read=False
        ).count()
        recent_notifications = Notification.objects.filter(
            exporter=request.user
        ).order_by('-created_at')[:5]

    context={
        'products':products,
        "unread_count": unread_count,
        "recent_notifications": recent_notifications,
    }
    return render(request,'index.html',context)


def static(request):
    if request.user.is_anonymous:
        return redirect('login')
    return render(request,'static.txt')

def loginuser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"username: {username}, password: {password}")

        user = authenticate(username=username, password=password)
        if user is not None:
            print(f"Authenticated user: {user.username}")
            try:
                cart_id = _cart_id(request)
                print(f"Session Cart ID: {cart_id}")
                session_cart = Cart.objects.get(cart_id=cart_id)
                session_cart_items = CartItem.objects.filter(cart=session_cart)
                print(f"Found {session_cart_items.count()} items in session cart")
                for item in session_cart_items:
                    print(f"Assigning item {item.product.name} to user {user.username}")
                    CartItem.objects.filter(id=item.id).update(user=user)
                    item.save()
            except Cart.DoesNotExist:
                print("No session cart found.")

            login(request, user)
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.userType == 'farmer':
                   if not FarmerProfile.objects.filter(farmer=request.user).exists():
                        return redirect('create_profile')
                   return redirect('farmer')  
                elif profile.userType == 'exporter':
                    return redirect('index')  
                else:
                    return redirect('analyst')
            except UserProfile.DoesNotExist:
                print("User profile not found.")
                pass
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def regester_user(request):
     if request.method == 'POST':
        name=request.POST.get('name')
        email=request.POST.get('mail')
        password=request.POST.get('password')
        usertype=request.POST.get('usertype')
        if usertype not in ['farmer', 'exporter','analyst']:
            return render(request, 'regester.html', {'error': 'Please select a valid user type.'})
        # Check if username or email already exists
        username = email.split('@')[0]
        # Check if username or email already exists
        if User.objects.filter(username=name).exists():
            return render(request, 'regester.html', {'error': 'Username already exists.'})
        elif User.objects.filter(email=email).exists():
            return render(request, 'regester.html', {'error': 'Email is already registered.'})
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=name
            )
            UserProfile.objects.create(user=user, userType=usertype)
            messages.success(request, "Regestration sucessful.")
            return redirect('login')  
        except IntegrityError:
            return render(request, 'regester.html', {'error': 'User registration failed due to a server error.'})
     return render(request,'regester.html')





def _cart_id(request):       #privatefunction to create cart_id based on session key
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart
def add_cart(request,product_id):
    if request.user.is_anonymous:
        return redirect('login')
    quantity = int(request.POST.get('quantity', 1))
    product=Product.objects.get(id=product_id)   # get product
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request)) # get cart based on cart_id present in session
    except:
        if Cart.DoesNotExist:
            cart=Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    try:
        cartitem=CartItem.objects.get(product=product,cart=cart)
        cartitem.quantity+=1
        messages.success(request, f"Updated quantity for {product.name}.")
    except:
        if CartItem.DoesNotExist:
            if request.user.is_authenticated:
                user = request.user
            else:
                user = None
            cartitem=CartItem.objects.create(user=user,product=product,quantity=quantity,cart=cart)
            messages.success(request, f"Added {product.name} to cart.")
        cartitem.save()
    return redirect('cart')
def remove_cart(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        try:
            cart_item = CartItem.objects.filter(user=request.user, product_id=product_id)
            cart_item.delete()
            print("Deleted successfully")
        except CartItem.DoesNotExist:
            print("No matching cart item found for user:", request.user)
    
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    if request.user.is_anonymous:
        return redirect('login')
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))

        if request.user.is_authenticated:
            # Show only items associated with this user
            cart_items = CartItem.objects.filter(cart=cart, user=request.user, is_active=True)
        else:
            # Show session-based items for guests
            cart_items = CartItem.objects.filter(cart=cart, user=None, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            cart_item.subtotal=cart_item.product.price * cart_item.quantity
    except ObjectDoesNotExist:
        cart_items = []
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items
    }
    return render(request, 'cart.html', context)
def update_cart(request, cart_item_id):
  if request.method == "POST":
        data = json.loads(request.body)
        quantity = int(data.get("quantity", 1))

        cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
        cart_item.quantity = quantity
        cart_item.save()

        # Recalculate totals
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, user=request.user, is_active=True)
        total = sum(item.product.price * item.quantity for item in cart_items)
        subtotal = cart_item.product.price * cart_item.quantity

        return JsonResponse({
            "success": True,
            "subtotal": subtotal,
            "total": total
        })

  return JsonResponse({"success": False}, status=400)
def checkout(request):
    if request.user.is_anonymous:
        return redirect('login')
    if request.method=='POST':
        try: 
            payment_method=request.POST.get('payment_method')
            item_json=request.POST.get('itemsjson','')
            name=request.POST.get('name','')
            email=request.POST.get('email','')
            phone=request.POST.get('phone','')
            address=request.POST.get('address','')
            city=request.POST.get('city','')
            state=request.POST.get('state','')
            postal_code=request.POST.get('zip_code','')
            # Extra test
            items = json.loads(item_json)
            product_ids = [int(item['product_id']) for item in items]
            print("Product IDs:", product_ids)
            products = Product.objects.filter(id__in=product_ids).select_related('owner')
            owners = []
            price=0;
            for product in products:
                if product.owner:
                    owners.append({
                        "username": product.owner.username,
                    })
            for product in products:
                print(product.owner)
            # order
            order=Order(item_json=item_json,name=name,email=email, phone=phone,address=address,city=city,state=state,postal_code=postal_code,product_owner=owners,buyer=request.user)
            order.save()
            #orederItem
            items = json.loads(item_json)
            for item in items:
                product = Product.objects.get(id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    farmer=product.owner,
                    quantity=item.get('quantity', 1),
                    subtotal=item.get('subtotal', 0)
                )
            #orderUpdate
            update=OrderUpdate(order_id=order.order_id,update_Desc='The order has been placed')
            update.save()
            #stripe
            items = json.loads(item_json)
            if payment_method=='stripe':
                print(payment_method)
                total = sum([float(item['subtotal']) for item in items])
                total_amount = int(total * 100)  
            # Create Stripe Checkout Session
                session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'pkr',
                        'product_data': {
                            'name': f'Order #{order.order_id}',
                        },
                        'unit_amount': total_amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(f'/checkout/success/?order_id={order.order_id}'),
                cancel_url=request.build_absolute_uri('/checkout/cancel/'),
                customer_email=email,
                metadata={"order_id": str(order.order_id)},
            )
                return redirect(session.url, code=303)
            return redirect(f'/checkout/success/?order_id={order.order_id}'
            )

        except Exception as e:
            return HttpResponse(f"Error saving order: {e}")
        return render(request, 'checkout.html', {'success': True,'order_id': order.order_id})
    return render(request,'checkout.html')

def checkout_success(request):
    order_id = request.GET.get('order_id')
    return render(request, 'checkout.html', {'success': True, 'order_id': order_id})

def checkout_cancel(request):
    return HttpResponse("Payment canceled.")

def productpage(request):
    if request.user.is_anonymous:
        return redirect('login')
    return render(request,'productpage.html')
def fruit(request):
    if request.user.is_anonymous:
        return redirect('login')
    context={
        'products':Product.objects.all()
    }
    return render(request,'fruit.html',context)


def vegitable(request):
    if request.user.is_anonymous:
        return redirect('login')
    context={
        'products':Product.objects.all()
    }
    return render(request,'vegitable.html',context)


def dryfruit(request):
    if request.user.is_anonymous:
        return redirect('login')
    context={
        'products':Product.objects.all()
    }
    return render(request,'dryfruit.html',context)


def addproduct(request):
    if request.user.is_anonymous:
        return redirect('login')
    if request.method == 'POST':
        name = request.POST.get('name')
        desc=request.POST.get('desc')
        price = request.POST.get('price')
        category = request.POST.get('category')
        subcategory = request.POST.get('subcategory')
        image_file = request.FILES.get('imageFile')
        image_url = request.POST.get('imageURL')
        stock=request.POST.get('stock')
        owner=request.user

        if not name or not price or not category or not subcategory:
            messages.error(request, "All fields except image are required.")
            return redirect('addproduct')

        try:
            product = Product(
                name=name,
                price=price,
                category=category,
                subcategory=subcategory,
                desc=desc,  
                data=date.today(),
                stock=stock,
                owner=owner
            )

            if image_file:
                product.image = image_file
            elif image_url:
                img_temp = NamedTemporaryFile(delete=True)
                with urllib.request.urlopen(image_url) as u:
                    img_temp.write(u.read())
                img_temp.flush()
                file_name = image_url.split("/")[-1]
                product.image.save(file_name, ContentFile(img_temp.read()))

            product.save()
            messages.success(request, f"Product '{product.name}' added successfully!")
        except Exception as e:
            messages.error(request, f"Failed to add product: {str(e)}")

        return redirect('addproduct')
    return render(request, 'addproduct.html')
# delete Product
def delete_product(request,pk):
    if request.method == "POST":
        product = get_object_or_404(Product, pk=pk, owner=request.user)  # Only delete if this user owns it
        product.delete()
        messages.success(request, f"Product '{product.name}' Removed sucessfully")
    return redirect('user_products')

def product_cart(request):
    if request.user.is_anonymous:
        return redirect('login')
    return render(request,'cart.html')


def product_checkout(request):
    if request.user.is_anonymous:
        return redirect('login')
    return render(request,'checkout.html')


def contact(request):
    if request.user.is_anonymous:
        return redirect('login')
    if request.method=='POST':
        try:
            name=request.POST.get('name')
            email=request.POST.get('email')
            message=request.POST.get('message')
            contact=Contact.objects.create(name=name,email=email,message=message)
            contact.save()
            message.success(request,'information send succefully')
            
        except:
            pass
    return render(request,'contact.html')



def pro(request):
      params={'product':Product.objects.all()}
      return render(request,'product.html',params)

def productdisplay(request,myid):
    if request.user.is_anonymous:
        return redirect('login')
    product = get_object_or_404(Product, id=myid)
    farmer = product.owner 
    # Aggregate farmer ratings
    farmer_rating = FarmerRating.objects.filter(farmer=farmer).aggregate(
        avg_rating=Avg("rating"),
        total_reviews=Count("id")
    )
    # Fetch all reviews for this farmer
    farmer_reviews = FarmerRating.objects.filter(farmer=farmer).select_related("buyer").order_by("-id")

    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:20]
    return render(request, 'productdisplay.html', {
        'product': product,
        'related_products': related_products,
        "farmer_rating": farmer_rating,
        "farmer_reviews": farmer_reviews})

def tracker(request):
    if request.user.is_anonymous:
        return redirect('login')
    if request.method == 'POST':
        order_id = request.POST.get('order_id', '')
        email = request.POST.get('email', '')

        try:
            # Make sure order_id is an integer
            order_id = int(order_id)

            # Check if the order exists with matching ID and email
            order = Order.objects.filter(order_id=order_id, email=email).first()
            if order:
                updates = OrderUpdate.objects.filter(order_id=order_id).order_by('timestamp')
                update_list = []

                for item in updates:
                    update_list.append({
                        'text': item.update_Desc,
                        'time': item.timestamp.strftime("%Y-%m-%d")
                    })

                return HttpResponse(json.dumps(update_list), content_type="application/json")
            else:
                # No matching order found
                return HttpResponse(json.dumps([]), content_type="application/json")

        except Exception as e:
            return HttpResponse(json.dumps([]), content_type="application/json")

    return render(request, 'tracker.html')


# search Functionalty
def search(request):
    
    keyword = request.GET.get('keyword', '').strip()
    category = request.GET.get('category', '').strip().lower()
    CATEGORY_ALIASES = {
        "fruit": ["fruit", "fruits", "friut", "fruitt", "fruites"],
        "vegetable": ["vegetable", "vegetables", "vegitable", "veg", "vegies"],
        "dryfruit": ["dryfruit", "dryfruits", "drufruit", "dry fruit", "dry-fruit"],
        "seed": ["seed", "seeds"],
    }
    products = Product.objects.all()
    if 'keyword' in request.GET:
        keyword=request.GET['keyword']
        if keyword:
            products=products.order_by('data').filter(Q(desc__icontains=keyword) | Q(name__icontains=keyword) | Q(category__icontains=keyword) |Q(subcategory=keyword))
    if category and category != "all":
        matched_category = None
        for key, aliases in CATEGORY_ALIASES.items():
            if category in aliases:
                matched_category = key
                break
    if matched_category:
            products = products.filter(category__iexact=matched_category)
    print('catagory:',products)
    product_count=products.count()
    context={
        'products':products,
        'searched': bool(keyword),
        'product_count': product_count,
        'selected_category': category,
        'keyword': keyword
        }
    return render(request,'search.html',context)

# Product of current user
def user_products(request):
    if request.user.is_anonymous:
       return redirect('login')
    user=request.user
    products=Product.objects.filter(owner=user)
    context={
        'products': products
    }
    return render(request,'user_products.html',context)

# Formers
def former(request):
    userprofile=UserProfile.objects.get(user=request.user)
    if userprofile.userType !='farmer':
         return HttpResponseForbidden("🚫 You don’t have permission to access this page.")
    activeproduct=Product.objects.filter(owner=request.user).count()
    full_name=(str(request.user.first_name)).upper()
    name="".join([part[0].upper() for part in full_name.split()])
    all_orders = Order.objects.filter(Q(product_owner__icontains=request.user.username)).count()
    # getting Price
    order_totals = {}
    revenue = Decimal('0')
    pending_count = 0
    order_statuses = {}
    orders = Order.objects.filter(product_owner__icontains=request.user.username)
    for order in orders:
        total_price_for_user = Decimal('0')
        try:
            items = json.loads(order.item_json) 
        except json.JSONDecodeError:
            pass
        for item in items:
            try:
                product_id = int(item.get('product_id', 0))
            except (ValueError, TypeError):
                continue
            if Product.objects.filter(id=product_id, owner=request.user).exists():
                price = Decimal(str(item.get('price', 0)))
                qty = Decimal(str(item.get('quantity', 0)))
                total_price_for_user += price * qty
                order_status=OrderUpdate.objects.filter(order_id=product_id)
                
                updates = OrderUpdate.objects.filter(order_id=order.order_id)  
                for update in updates:
                    order_statuses[order.order_id] = update.order_status
                    if update.order_status == 'pending':
                        pending_count += 1
        order_totals[order.order_id]=total_price_for_user
        revenue+=total_price_for_user
        # print( order_statuses)
    ## products of current user
    user_products=Product.objects.filter(owner=request.user).order_by('-data')[:5]
    # orders
    order=Order.objects.filter(Q(product_owner__icontains=request.user.username)).order_by('-created_at')[:5]
    # crops
    crops = CropPlan.objects.filter(farmer=request.user)
    
    # weather data
    profile = get_object_or_404(FarmerProfile, farmer=request.user)
    weather_data = None
    if profile.lat and profile.lon:
        try:
            weather_data = get_weather(profile.lat, profile.lon)
            print("weather data: ",weather_data)
        except Exception as e:
            print("⚠️ Weather API error:", e)
    # crop advice
    # crop_advices = []
    # for crop in crops:
    #     ai_advice = None
    #     if weather_data:
    #         try:
    #             data = query_rag(
    #                 stage=crop.current_stage,
    #                 crop_name=crop.crop_name,
    #                 # come from profile,
    #                 land_size=profile.land_size,
    #                 soil_type=profile.soil_type,
    #                 water_source=profile.water_source,
    #                 Agroecological_zone=profile.Agroecological_zone,
    #                 location=profile.location,
    #                 #  crop-specific
    #                 soil_moisture='40%',
    #                 last_ai_advice=crop.last_ai_advice,
    #                 Soil_pH=2.5,
    #                 # weather
    #                 humidity=weather_data.get("humidity"),
    #                 pressure=weather_data.get("pressure"),
    #                 wind_speed=weather_data.get("wind_speed"),
    #                 temperature=weather_data.get("temperature"),
    #                 last_rain=weather_data.get("last_rain"),
    #                 next_rain=weather_data.get("next_rain"),
    #             )
    #             ai_advice = data.get("answer")
    #             crop.last_ai_advice = ai_advice
    #             crop.save()
    #         except RAGError as e:
    #             ai_advice = f"⚠️ Error fetching AI advice: {e}"

    #     crop_advices.append({
    #         "crop": crop,
    #         "advice": ai_advice
    #     })
    # Crop outcome
    outcomes = CropOutcome.objects.filter(crop__farmer=request.user)
    crop_stats = {
        "total": outcomes.count(),
        "success": outcomes.filter(status="success").count(),
        "damaged": outcomes.filter(status="damaged").count(),
        }

    context={
        'activeproducts': activeproduct,
        'full_name' : full_name,
        'name' : name,
        'all_orders' : all_orders,
       # 'total_price' : total_price_for_user,
        'user_products' : user_products,
        'orders' : order,
        'revenue' : revenue,
        'order_totals': order_totals,
        'pending_count' : pending_count,
        'order_statuses' : order_statuses,
        "crops": crops,
        "weather": weather_data,
        # "crop_advices": crop_advices,
        "crop_stats" :crop_stats
    }
   

    if request.method=="POST":
        message=request.POST.get('message-text')
        name=request.user
        email=request.user.email
        if message.strip(): 
            try:
                Contact.objects.create(name=name,email=email,message=message)
                messages.success(request, "✅ Your message was sent successfully!")
            except:
                messages.error(request, "❌ Please enter a message before sending.")
    return render(request,'farmer.html',context)
   

# order for farmer
def farmer_orders(request):
    order_totals = {}
    revenue = Decimal('0')
    order_statuses = {}
    orders = Order.objects.filter(product_owner__icontains=request.user.username)
    for order in orders:
        total_price_for_user = Decimal('0')
        try:
            items = json.loads(order.item_json)  # Parse items list
        except json.JSONDecodeError:
            pass
        for item in items:
            try:
                product_id = int(item.get('product_id', 0))
            except (ValueError, TypeError):
                continue
            if Product.objects.filter(id=product_id, owner=request.user).exists():
                price = Decimal(str(item.get('price', 0)))
                qty = Decimal(str(item.get('quantity', 0)))
                total_price_for_user += price * qty
                updates = OrderUpdate.objects.filter(order_id=order.order_id)  
                for update in updates:
                    order_statuses[order.order_id] = update.order_status
        order_totals[order.order_id]=total_price_for_user
        revenue+=total_price_for_user
       
    all_orders = Order.objects.filter(Q(product_owner__icontains=request.user.username)).count()
    context={
    'orders':orders,
    'order_totals':order_totals,
    'all_orders' : all_orders,
    'order_statuses' : order_statuses
    }
    return render(request,'farmer_orders.html',context)

def update_order_status(request, order_id):
    if request.method == "POST":
        new_status = request.POST.get('order_status')
        order_update = get_object_or_404(OrderUpdate, order_id=order_id)
        order_update.order_status = new_status
        order_update.save()
    return redirect('farmer')


def rate_farmer(request, order_item_id):
    order_item = get_object_or_404(OrderItem, pk=order_item_id, order__buyer=request.user)

    if request.method == 'POST':
        rating_value = int(request.POST.get('rating'))
        review_text = request.POST.get('review', '')

        FarmerRating.objects.update_or_create(
            buyer=request.user,
            order_item=order_item,
            defaults={
                'farmer': order_item.farmer,
                'rating': rating_value,
                'review': review_text
            }
        )
        messages.success(request, "Thank you for your feedback!")
        return redirect('order_history')

    return render(request, 'rate-farmer.html', {'order_item': order_item})

def order_history(request):
    orders = (
        Order.objects
        .filter(buyer=request.user)  
        .prefetch_related('items__farmer', 'items__product', 'items__rating')
        .order_by('created_at')
    )
    print(orders)
    return render(request, 'order_history.html', {'orders': orders})



def exporter_notifications(request):
    notifications = Notification.objects.filter(exporter=request.user).order_by('-created_at')
    print(notifications)
    notifications.update(is_read=True)
    return render(request, "exporter_notifications.html", {"notifications": notifications})

#################### Sending Data to colab ####################
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from .rag_client import query_rag, RAGError

#################### crops tracker ####################

def create_profile(request):
    if request.method=='POST':
        FarmerProfile.objects.update_or_create(
          farmer=request.user,
          defaults={
            "land_size": request.POST.get("land_size"),
            "soil_type": request.POST.get("soil_type"),
            "water_source": request.POST.get("water_source"),
            # "temperature":34,    # temperature will come from iot devices
            # "soil_moisture":'80%',  # soil mosture will come from iot devices 
            'location':request.POST.get('location'),
            'Agroecological_zone':request.POST.get('region'),
        }
    )
        messages.success(request, "✅ Profile created sucessfully!")
        return redirect("farmer")
    
    return render(request, "farmer_profile.html")
@require_POST
def add_crop(request):
    profile = get_object_or_404(FarmerProfile, farmer=request.user)
    CropPlan.objects.create(
        farmer=request.user,
        profile=profile,
        crop_name=request.POST.get("crop_name"), 
    )
    return redirect("farmer")

@require_POST
def select_crop(request, crop_id):
    crop = get_object_or_404(CropPlan, id=crop_id, farmer=request.user)
    crop_field=request.POST.get('crop_field')
    harvesting_date_str = request.POST.get("harvesting_date")
    harvesting_date = None
    if harvesting_date_str:
        harvesting_date = datetime.datetime.strptime(harvesting_date_str, "%Y-%m-%d").date()
    chosen_crop = request.POST.get("chosen_crop")
    crop_variety=request.POST.get('chosen_cropvariety')
    print(crop_variety)
    if chosen_crop:
        crop.crop_name = chosen_crop
        crop.crop_variety=crop_variety
        crop.crop_field=crop_field
        crop.current_stage = 2   # move to next stage
        crop.harvesting_date=harvesting_date
        crop.save()
        return JsonResponse({"ok": True, "crop_name": chosen_crop, "crop_veriety": crop_variety , "stage":crop.current_stage})
    else:
        return JsonResponse({"ok": False, "error": "No crop selected"}, status=400)

@require_POST
def ask_rag(request, crop_id):
    try:
        crop = get_object_or_404(CropPlan, id=crop_id, farmer=request.user)
        farmerprofile=get_object_or_404(FarmerProfile,farmer=request.user)
        # weather Data
        weather_data = None
        if farmerprofile.lat and farmerprofile.lon:
            weather_data = get_weather(farmerprofile.lat, farmerprofile.lon)
        farmer_data = {
            "stage": int(crop.current_stage),
            "crop_name": crop.crop_name,   # will be None/blank at stage 1
            'last_ai_advice':crop.last_ai_advice,
            "land_size": farmerprofile.land_size,
            "location":farmerprofile.location,
            'Agroecological_zone':farmerprofile.Agroecological_zone,
            "soil_type": farmerprofile.soil_type,
            "water_source": farmerprofile.water_source,
            # temp will be taken from iot devices
            "soil_moisture": '50%', # soil mosture will be taken from iot devices 
            'Soil_pH' :2  # Soil pH will come from iot devices
        }
        
        # Merge weather data if available
        if weather_data:
            farmer_data.update({
                "temperature": weather_data["temperature"],
                "humidity": weather_data["humidity"],
                "pressure": weather_data['pressure'],
                "wind_speed": weather_data['wind_speed'],
                "last_rain": weather_data["last_rain"],
                "next_rain": weather_data["next_rain"],
            })

        print("➡️ Sending payload to Colab:", farmer_data)
        result = query_rag(**farmer_data)
        print("✅ Colab response:", result)

        # Save AI advice
        crop.last_ai_advice = result.get("answer")
        crop.save()

        # Only auto-advance if stage > 1
        if result.get("ok") and crop.current_stage > 1 and crop.current_stage < 7:
            crop.next_stage()

        return JsonResponse(result)

    except RAGError as e:
        print("❌ RAGError:", e)
        return JsonResponse({"ok": False, "error": str(e)}, status=502)
    except Exception as e:
        import traceback
        print("❌ Unexpected error:", e)
        print(traceback.format_exc())
        return JsonResponse({"ok": False, "error": "Server crash, check logs"}, status=500)


@require_POST
def advance_stage(request, crop_id):
    crop = get_object_or_404(CropPlan, id=crop_id, farmer=request.user)
    if crop.current_stage < 7:
        crop.current_stage += 1
        crop.save()
    return redirect('farmer')

def crop_advice(request, crop_id):
    crop = get_object_or_404(CropPlan, id=crop_id, farmer=request.user)
    return render(request, "crop_advice.html", {"crop": crop})

#### download response as pdf ############
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
def download_advice_pdf(request, crop_id):
    crop = get_object_or_404(CropPlan, id=crop_id, farmer=request.user)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="{crop.crop_name}_advice.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, f"AI Farming Advice for {crop.crop_name}")
    p.drawString(100, 730, f"Stage: {crop.get_current_stage_display()}")

    text = p.beginText(100, 700)
    text.setFont("Helvetica", 11)
    advice = crop.last_ai_advice or "No advice available."
    for line in advice.splitlines():
        text.textLine(line)
    p.drawText(text)

    p.showPage()
    p.save()
    return response

def delete_crop(request, crop_id):
    crop = get_object_or_404(CropPlan, id=crop_id, farmer=request.user)
    
    if request.method == "POST":
        crop.delete()
        messages.success(request, "Crop plan deleted successfully ✅")
        return redirect("farmer")  

    return render(request, "confirm_delete_crop.html", {"crop": crop})

#Crop record 
def record_outcome(request, crop_id):
    crop = get_object_or_404(CropPlan, id=crop_id, farmer=request.user)

    # if already exists → edit outcome
    try:
        outcome = crop.outcome
    except CropOutcome.DoesNotExist:
        outcome = None

    if request.method == "POST":
        form = CropOutcomeForm(request.POST, instance=outcome)
        if form.is_valid():
            outcome = form.save(commit=False)
            outcome.crop = crop
            outcome.save()
            return redirect("farmer")  # go back to farmer dashboard
    else:
        form = CropOutcomeForm(instance=outcome)

    return render(request, "record_outcome.html", {"form": form, "crop": crop})


##### Previouse Crops #########
def previous_crops(request):
    previous_crops = CropPlan.objects.filter(
        farmer=request.user,
        current_stage=7,   # stage = Post-Harvesting
        outcome__isnull=False
    ).order_by("-harvesting_date")

    return render(request, "previous_crops.html", {"previous_crops": previous_crops})

def analyst(request):
    if request.user.is_anonymous:
        return redirect('login')
    userprofile=UserProfile.objects.get(user=request.user)
    if userprofile.userType !='analyst':
         return HttpResponseForbidden("🚫 You don’t have permission to access this page.")
    return render(request,'analyst.html')

    
def all_previous_crop(request):
    if request.user.is_anonymous:
        return redirect('login')
    previous_crops=CropOutcome.objects.all()
    
    context={
        'previous_crops' : previous_crops
    }
    return render(request,'all_previous_crops.html',context)
def current_crops(request):
    if request.user.is_anonymous:
        return redirect('login')
    current_crops=CropPlan.objects.all()
    context={
        'current_crops' : current_crops
    }
    return render(request,'current_crops.html',context)
