import streamlit as st
from kafka import KafkaConsumer
import json
import time

st.title("Real-Time Gesture Dashboard")

# Create consumer ONCE (important fix)
if "consumer" not in st.session_state:
    st.session_state.consumer = KafkaConsumer(
        'gesture_topic',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True
    )

consumer = st.session_state.consumer

placeholder = st.empty()

# Non-blocking polling loop
while True:
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
        with placeholder.container():
            st.write("Waiting for data...")

    time.sleep(1)

    # prevents Streamlit crash loop handling
    st.rerun()