import streamlit as st
import cv2
import numpy as np
from keras.models import load_model
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
from kafka import KafkaProducer
import json

# Load model
model = load_model("Model/keras_model.h5")

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

labels = ["1", "2", "3", "Heart", "Ok", "SOS", "thankYou"]


class GestureProcessor(VideoProcessorBase):
    def __init__(self):
        self.prev_pred = ""

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Resize for faster processing
        img = cv2.resize(img, (640, 480))

        # Dummy crop (replace with hand detection later)
        h, w, _ = img.shape
        imgCrop = img[100:400, 150:450]

        try:
            # Resize to model input
            imgInput = cv2.resize(imgCrop, (224, 224))
            imgInput = imgInput / 255.0
            imgInput = np.reshape(imgInput, (1, 224, 224, 3))

            preds = model.predict(imgInput, verbose=0)
            classIndex = np.argmax(preds)
            confidence = np.max(preds)

            if confidence > 0.8:
                label = labels[classIndex]

                # Send to Kafka
                producer.send("gestures", {"gesture": label})

                self.prev_pred = label

                cv2.putText(img, f"{label} ({confidence:.2f})",
                            (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)

        except:
            pass

        return img


st.title("Gesture Recognition Dashboard")

webrtc_streamer(
    key="gesture",
    video_processor_factory=GestureProcessor
)