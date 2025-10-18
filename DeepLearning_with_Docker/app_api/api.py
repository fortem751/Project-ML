from fastapi import FastAPI, UploadFile, File
from PIL import Image
import torch
from torchvision import models, transforms
from io import BytesIO

# --- 1. SETUP ---
# Pre-trained model and transformation pipeline
model = models.resnet18(pretrained=True)
model.eval()

# Image preprocessing
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# Load ImageNet Class Labels for human-readable output
# NOTE: The file 'imagenet_classes.txt' must be in the same directory!
try:
    # This reads the file content and cleans up the index: label format
    with open("imagenet_classes.txt") as f:
        # Assuming the file format is simple: 'index: label'
        classes = [line.strip().split(': ')[1].strip("'") for line in f]
except FileNotFoundError:
    # Fallback if the label file is missing
    classes = [f"Class Index {i}" for i in range(1000)]
    print("WARNING: Could not find imagenet_classes.txt. Using index numbers.")


app = FastAPI()

# --- 2. API ENDPOINT ---


@app.post("/predict/")
async def predict_image(file: UploadFile = File(...)):
    # Read the image data from the upload
    image_data = await file.read()
    image = Image.open(BytesIO(image_data))

    # Preprocess and infer
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)

    with torch.no_grad():
        output = model(input_batch)

    # Get the predicted class index and probability
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    top_p, top_class_index = probabilities.topk(1, dim=0)

    # *** NEW: Use the loaded 'classes' list to get the object name ***
    predicted_class_name = classes[top_class_index.item()]

    prediction = (f"Predicted Object: {predicted_class_name}, "
                  f"Probability: {top_p.item():.4f}")

    return {"prediction": prediction}

# Health check endpoint


@app.get("/health")
def health_check():
    return {"status": "ok", "model": "ResNet18"}
