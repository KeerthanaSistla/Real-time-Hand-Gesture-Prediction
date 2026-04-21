from kafka import KafkaProducer
import json

class GestureProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            linger_ms=10
        )

    def send_gesture(self, gesture, confidence):
        data = {
            "gesture": gesture,
            "confidence": float(confidence)
        }

        try:
            self.producer.send("gesture_topic", value=data)
        except Exception as e:
            print("Kafka Error:", e)