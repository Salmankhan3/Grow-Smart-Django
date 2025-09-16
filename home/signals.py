# home/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from home.models import Product
from streaming.kafka_producer import send_product_to_kafka


@receiver(post_save, sender=Product)
def product_created(sender, instance, created, **kwargs):
    if created:  # Only on new product creation
        print(f"🚀 Signal fired for product {instance.name}")
        send_product_to_kafka(instance)
