# streaming/run_exporter_consumer.py
from confluent_kafka import Consumer, KafkaException
import sys, os, django
import json
import uuid

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Grow_Smart.settings")
django.setup()
from home.models import Notification, UserProfile
conf = {
    'bootstrap.servers': 'localhost:9092',
    #  always create a fresh consumer group so offsets never get stuck
    'group.id': f'exporter-group-{uuid.uuid4()}',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['products'])

try:
    print("🚚 Exporter listening for products...")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        product = json.loads(msg.value().decode("utf-8"))

        # Debug print
        print("🔍 RAW received:", product)

        # Pretty print with farmer name
        print(
            f"📦 Product received: {product['name']} | "
            f"Qty: {product['quantity']} | "
            f"Price: {product['price']} | "
            f"👨‍🌾 Farmer: {product.get('owner_username', 'Unknown')}"
        )
        message = f" Farmer {product.get('owner_username', 'Unknown')} listed {product['name']} | Qty: {product['quantity']} | Price: {product['price']}"
        print(message)
        exporters = UserProfile.objects.filter(userType="exporter")
        for profile in exporters:
            Notification.objects.create(exporter=profile.user, message=message)

        print("📢 Notification saved for exporters:", message)

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
