# streaming/kafka_producer.py
from confluent_kafka import Producer
import json


producer_conf = {
    'bootstrap.servers': 'localhost:29092'
}

producer = Producer(producer_conf)
TOPIC = "products"

def send_product_to_kafka(product):
    """Send product details to Kafka topic"""
    data = {
        "id": product.id,
        "name": product.name,
        "quantity": product.stock,
        "price": float(product.price),
        "owner_id": product.owner.id if product.owner else None,
        "owner_username": product.owner.username if product.owner else "Unknown"

    }
    print("🔍 DEBUG - Sending to Kafka:", data)
    producer.produce(
        TOPIC,
        key=str(product.id),
        value=json.dumps(data).encode("utf-8")
    )
    producer.flush()
    print(f"✅ Sent product {product.name} by {data['owner_username']} to Kafka")
