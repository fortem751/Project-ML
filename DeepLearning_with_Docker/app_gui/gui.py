# app_gui/gui.py
import gradio as gr
import requests
import os
import io

# The API URL must use the service name 'api' and the port 8000

API_URL = "http://api:8000/predict/"


def query_api(image):
    if image is None:
        return "Please upload an image."

    # Convert Gradio image (numpy array) to bytes/file-like object

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Make the request to the FastAPI container
    files = {'file': ('image.png', img_byte_arr, 'image/png')}

    try:
        response = requests.post(API_URL, files=files)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Get prediction result from the JSON response
        result = response.json().get("prediction", "No prediction found.")
        return result
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the Inference API. Is the 'api' container running?"
    except Exception as e:
        return f"An error occurred: {e}"


# Gradio Interface Setup
iface = gr.Interface(
    fn=query_api,
    inputs=gr.Image(type="pil", label="Upload Image"),
    outputs="text",
    title="Deep Learning Inference with Docker Compose",
    description="Upload an image to get a prediction from the FastAPI container."
)

# Launch the interface on 0.0.0.0 so it's accessible outside the container
iface.launch(server_name="0.0.0.0", server_port=7860)
