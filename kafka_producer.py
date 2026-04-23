import json
import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = "gesture_topic"

gestures = ["1", "2", "3", "Heart", "Ok", "SOS", "ThankYou"]

print("Sending gesture data to Kafka...")

while True:
    data = {
        "gesture": random.choice(gestures),
        "confidence": round(random.uniform(0.7, 0.99), 2),
        "timestamp": time.time()
    }

    producer.send(topic, value=data)
    print("Sent:", data)

    time.sleep(1)