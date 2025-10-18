import gradio as gr
from PIL import Image
import torch
from torchvision import models, transforms
import io
import traceback  # Import traceback to capture detailed errors

# --- 1. MODEL SETUP ---
# Load the pre-trained ResNet18 model and set to evaluation mode
model = models.resnet18(pretrained=True)
model.eval()

# Image preprocessing pipeline (matches the PyTorch standard for ImageNet models)
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# Load ImageNet Class Labels for human-readable output
# FIX: Robust file reading to ignore empty or malformed lines.
try:
    classes = []
    with open("imagenet_classes.txt") as f:
        for line in f:
            line = line.strip()
            # Only process lines that contain the separator and are not empty
            if ': ' in line:
                # Splits the line and extracts the label name (index 1)
                label_name = line.split(': ')[1].strip("'")
                classes.append(label_name)
except FileNotFoundError:
    # Fallback if the label file is missing
    classes = [f"Class Index {i}" for i in range(1000)]
    print("WARNING: Could not find imagenet_classes.txt. Using index numbers.")


# --- 2. INFERENCE FUNCTION ---
def classify_image(input_image: Image.Image):
    """
    Takes a PIL Image object, runs it through the ResNet18 model, 
    and returns the human-readable prediction or a detailed error message.
    """
    if input_image is None:
        return "Please upload an image."

    try:
        # Preprocess the image
        input_tensor = preprocess(input_image)
        input_batch = input_tensor.unsqueeze(0)  # Add a batch dimension

        # Run inference without gradient tracking (faster)
        with torch.no_grad():
            output = model(input_batch)

        # Calculate probabilities and find the top prediction
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top_p, top_class_index = probabilities.topk(1, dim=0)

        # Get the human-readable name and format the output
        # Ensure the index is within the bounds of the classes list
        if top_class_index.item() < len(classes):
            predicted_class_name = classes[top_class_index.item()]
        else:
            predicted_class_name = f"Index {top_class_index.item()} out of bounds."

        # Return the prediction as a nicely formatted string
        prediction_text = (
            f"Predicted Object: {predicted_class_name}\n"
            f"Confidence: {top_p.item():.4f}"
        )

        return prediction_text

    except Exception as e:
        # If any error occurs during processing, return the detailed traceback
        error_message = f"RUNTIME ERROR DURING INFERENCE:\n{str(e)}\n\n"
        error_message += "--- Traceback ---\n"
        error_message += traceback.format_exc()
        return error_message


# --- 3. GRADIO INTERFACE ---

# Define the input and output components
input_image = gr.Image(type="pil", label="Upload an Image for Classification")
# Increased lines for error display
output_label = gr.Textbox(label="Model Prediction", lines=8)

# Create the Gradio Interface
gr.Interface(
    fn=classify_image,
    inputs=input_image,
    outputs=output_label,
    title="ResNet18 Image Classification Demo (AIIA Deployment)",
    description="Upload an image to classify it using a pre-trained PyTorch ResNet18 model.",
    allow_flagging="never",
    theme="soft"
).launch()
