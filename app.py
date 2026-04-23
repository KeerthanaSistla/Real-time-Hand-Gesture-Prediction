from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import cv2
import math
import time
import json

from tensorflow.keras.models import load_model
from cvzone.HandTrackingModule import HandDetector

# Kafka
from kafka import KafkaProducer

app = Flask(__name__)

# =========================
# LOAD MODEL
# =========================
model = load_model("Model/keras_model.h5")

labels = ["1", "2", "3", "Heart", "Ok", "SOS", "thankYou"]

# =========================
# HAND DETECTOR SETTINGS
# =========================
detector = HandDetector(maxHands=1)
offset = 20
imgSize = 300

# =========================
# KAFKA PRODUCER SETUP
# =========================
try:
    producer = KafkaProducer(
        bootstrap_servers='172.29.110.220',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        linger_ms=10
    )
    print("✅ Kafka Producer Connected")
except Exception as e:
    producer = None
    print("⚠️ Kafka not connected:", e)


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/predict", methods=["POST"])
def predict():

    if "image" not in request.files:
        return jsonify({"error": "No image received"}), 400

    file = request.files["image"]

    img = cv2.imdecode(
        np.frombuffer(file.read(), np.uint8),
        cv2.IMREAD_COLOR
    )

    # =========================
    # HAND DETECTION
    # =========================
    hands, img = detector.findHands(img)

    if not hands:
        return jsonify({
            "gesture": "No Hand Detected",
            "confidence": 0,
            "probabilities": {}
        })

    hand = hands[0]
    x, y, w, h = hand['bbox']

    # =========================
    # CREATE WHITE BACKGROUND
    # =========================
    imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255

    imgCrop = img[
        max(0, y - offset):y + h + offset,
        max(0, x - offset):x + w + offset
    ]

    aspectRatio = h / w

    # =========================
    # RESIZE (SAME AS TRAINING)
    # =========================
    if aspectRatio > 1:
        k = imgSize / h
        wCal = math.ceil(k * w)
        imgResize = cv2.resize(imgCrop, (wCal, imgSize))
        wGap = math.ceil((imgSize - wCal) / 2)
        imgWhite[:, wGap:wCal + wGap] = imgResize
    else:
        k = imgSize / w
        hCal = math.ceil(k * h)
        imgResize = cv2.resize(imgCrop, (imgSize, hCal))
        hGap = math.ceil((imgSize - hCal) / 2)
        imgWhite[hGap:hCal + hGap, :] = imgResize

    # =========================
    # MODEL PREDICTION
    # =========================
    imgInput = cv2.resize(imgWhite, (224, 224))
    imgInput = imgInput.astype(np.float32) / 255.0
    imgInput = np.expand_dims(imgInput, axis=0)

    preds = model.predict(imgInput, verbose=0)[0]

    class_id = int(np.argmax(preds))
    confidence = float(np.max(preds))

    gesture = labels[class_id]

    # =========================
    # SEND TO KAFKA
    # =========================
    if producer:
        try:
            producer.send("gesture_topic", {
                "gesture": gesture,
                "confidence": confidence * 100,
                "timestamp": time.time()
            })
        except Exception as e:
            print("Kafka Send Error:", e)

    # =========================
    # RESPONSE
    # =========================
    probabilities = {
        labels[i]: float(preds[i]) * 100
        for i in range(len(labels))
    }

    return jsonify({
        "gesture": gesture,
        "confidence": confidence * 100,
        "probabilities": probabilities
    })


if __name__ == "__main__":
    app.run(debug=True)