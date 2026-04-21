import streamlit as st
from kafka import KafkaConsumer
import json
import time

st.title("Real-Time Gesture Dashboard")

consumer = KafkaConsumer(
    'gesture',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest',
    enable_auto_commit=True
)

placeholder = st.empty()

messages = consumer.poll(timeout_ms=1000)

if messages:
    for tp, msgs in messages.items():
        for message in msgs:
            data = message.value

            gesture = data.get("gesture", "N/A")
            confidence = data.get("confidence", 0)

            with placeholder.container():
                st.subheader("Current Gesture")
                st.write(f"Gesture: {gesture}")
                st.write(f"Confidence: {confidence:.2f}")
else:
    st.write("Waiting for data...")

time.sleep(1)
st.rerun()
