import streamlit as st
import cv2
import numpy as np
from keras.models import load_model
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
from kafka import KafkaProducer
import json

model = load_model("Model/keras_model.h5")

labels = ["1", "2", "3", "Heart", "Ok", "SOS", "thankYou"]

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

class GestureProcessor(VideoProcessorBase):

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # =========================
        # FIX: crop hand region
        # =========================
        h, w, _ = img.shape
        img = img[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]

        img = cv2.resize(img, (224, 224))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        preds = model.predict(img, verbose=0)

        class_id = np.argmax(preds)
        confidence = np.max(preds)

        if confidence > 0.8:
            label = labels[class_id]

            producer.send("gesture_topic", {
                "gesture": label,
                "confidence": float(confidence)
            })

            cv2.putText(frame.to_ndarray(format="bgr24"),
                        f"{label} ({confidence:.2f})",
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

        return frame


st.title("Gesture Recognition Dashboard")

webrtc_streamer(
    key="gesture",
    video_processor_factory=GestureProcessor
)