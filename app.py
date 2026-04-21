from flask import Flask, request, jsonify
import numpy as np
import cv2
from tensorflow.keras.models import load_model
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

model = load_model("Model/keras_model.h5")

labels = ["1", "2", "3", "Heart", "Ok", "SOS", "thankYou"]

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image received"}), 400

    file = request.files["image"]

    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    preds = model.predict(img)
    class_id = np.argmax(preds)
    confidence = float(np.max(preds))

    return jsonify({
        "gesture": labels[class_id],
        "confidence": confidence
    })

if __name__ == "__main__":
    app.run(debug=True)