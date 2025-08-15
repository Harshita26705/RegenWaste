import gradio as gr
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image

# --- Load model and labels ---
model = load_model("Resources/Model/keras_model.h5")

with open("Resources/Model/labels.txt", "r") as f:
    labels = [line.strip().split(' ', 1)[1] for line in f.readlines()]  # get only label name

# --- Mapping: fine label -> category ---
label_to_category = {
    "Nothing": "Residual Waste",
    "Metal": "Recyclable Waste",
    "Plastic": "Recyclable Waste",
    "Paper": "Recyclable Waste",
    "Ewaste": "Hazardous Waste",
    "Leaf": "Organic Waste",
    "Wood": "Organic Waste",
    "Food": "Organic Waste",
    "Hazardous": "Hazardous Waste",
    "Fabric": "Residual Waste"
}

# --- Category -> Bin Image Path ---
bin_image_map = {
    "Recyclable Waste": "Resources/Bins/1.png",
    "Residual Waste": "Resources/Bins/2.png",
    "Organic Waste": "Resources/Bins/3.png",
    "Hazardous Waste": "Resources/Bins/4.png"
}

# --- Preprocessing ---
def preprocess_image(image):
    image = image.resize((224, 224))  # Match model input
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

# --- Prediction Logic ---
def classify_waste(image):
    preprocessed = preprocess_image(image)
    prediction = model.predict(preprocessed)[0]
    predicted_index = int(np.argmax(prediction))
    predicted_label = labels[predicted_index]  # e.g., "Leaf"

    category = label_to_category.get(predicted_label, "Residual Waste")
    bin_image = bin_image_map.get(category, "Resources/Bins/2.png")
    confidence = round(prediction[predicted_index] * 100, 2)

    return image, "➡️", f"{predicted_label} → {category} ({confidence}%)", bin_image

# --- UI ---
with gr.Blocks(css="""
body {
  background-image: url('file/Resources/background.png');
  background-size: cover;
  background-repeat: no-repeat;
  background-attachment: fixed;
}
""") as app:

    gr.Markdown("<h1 style='text-align:center; color:white;'>♻️ RegenWaste Classifier</h1>")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="📸 Upload Waste Image")

        with gr.Column():
            arrow = gr.Textbox(value="", show_label=False, interactive=False)
            prediction = gr.Textbox(label="🧠 Predicted Waste Type", interactive=False)

        with gr.Column():
            bin_output = gr.Image(label="🗑️ Recommended Bin")

    classify_btn = gr.Button("🔍 Classify Waste")

    classify_btn.click(
        fn=classify_waste,
        inputs=image_input,
        outputs=[image_input, arrow, prediction, bin_output]
    )

app.launch()
