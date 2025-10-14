# app_api/api.py
from fastapi import FastAPI, UploadFile, File
from PIL import Image
import torch
from torchvision import models, transforms
from io import BytesIO

# --- 1. SETUP ---
# Pre-trained model and transformation pipeline
# NOTE: We'll keep the model simple for the guide
model = models.resnet18(pretrained=True)
model.eval()

# Image preprocessing
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

app = FastAPI()

# --- 2. API ENDPOINT ---
@app.post("/predict/")
async def predict_image(file: UploadFile = File(...)):
    # Read the image data from the upload
    image_data = await file.read()
    image = Image.open(BytesIO(image_data))
    
    # Preprocess and infer
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)  # create a mini-batch as expected by the model
    
    with torch.no_grad():
        output = model(input_batch)
    
    # Get the predicted class index (simple example)
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    top_p, top_class = probabilities.topk(1, dim=0)
    
    # This is a placeholder for a real class name list
    # In a real app, you'd load a class mapping file (e.g., ImageNet classes)
    prediction = f"Predicted Class Index: {top_class.item()}, Probability: {top_p.item():.4f}"

    return {"prediction": prediction}

# You can add a simple health check endpoint too
@app.get("/health")
def health_check():
    return {"status": "ok", "model": "ResNet18"}