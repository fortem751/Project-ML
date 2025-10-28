from flask import Flask, request, jsonify
# from ultralytics import YOLO  # REMOVED: No longer using local YOLO
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import time
import requests  # ADDED: Required for making external API calls
import os  # Added os import for os.remove in __main__

app = Flask(__name__)
# Load the YOLOv8 Nano model once when the server starts
# model = YOLO('yolov8n.pt') # NO LONGER USED
PERSON_CLASS_ID = 0
OUTPUT_CSV = "az_ai_results.csv"  # Changed CSV name for Part 4 results

# --- AZURE CONFIGURATION (Task 4.1 Output) ---
# IMPORTANT: REPLACE THESE PLACEHOLDERS with your actual values from the Azure Portal
AZURE_VISION_ENDPOINT = "https://azimgprocessing1.cognitiveservices.azure.com/"
AZURE_VISION_KEY = "AZURE_VISION_KEY "

# Azure's Image Analysis URL to get Tags and Objects (looking for 'person')
# Use the correct API version for the Computer Vision Analyze Image operation (v3.2 is common)
AZURE_VISION_URL = f"{AZURE_VISION_ENDPOINT}/vision/v3.2/analyze?visualFeatures=Tags,Objects&language=en"

# --- Placeholder for VM Performance Metrics (remains the same for Task 4.3) ---
# ... (get_performance_metrics and log_vm_data functions are unchanged) ...


def get_performance_metrics(proc_time):
    """Simulated collection of VM resource metrics."""
    # Placeholder values for demonstration/initial logging
    # CPU should be lower since it's just making an HTTP call
    cpu_util = np.random.uniform(10, 30)
    mem_used = np.random.uniform(100, 200)
    # Bandwidth remains high for sending the image
    bandwidth = np.random.uniform(500, 1000)
    cost = proc_time * (0.0001 / 3600)
    return cpu_util, mem_used, cost, bandwidth


def log_vm_data(timestamp, count, proc_time, cpu_util, mem_used, cost, bandwidth):
    """Logs results and performance metrics. (Ensure 'proc_time_s' is renamed to 'response_time_s' in final code)"""
    try:
        # Check if the file exists to determine if a header is needed
        write_header = not pd.io.common.file_exists(OUTPUT_CSV)

        # NOTE: Using 'proc_time_s' here to match your old server.py,
        # but your analysis script expects 'response_time_s'. Ensure consistency!
        df = pd.DataFrame([{'timestamp': timestamp, 'people_count': count, 'proc_time_s': proc_time,
                            'cpu_util_%': cpu_util, 'mem_used_mb': mem_used,
                            'cost_unit': cost, 'bandwidth_kb': bandwidth}])
        df.to_csv(OUTPUT_CSV, mode='a', header=write_header, index=False)
    except Exception as e:
        print(f"Error logging data on VM: {e}")


@app.route('/process_frame', methods=['POST'])
def process_frame():
    # 1. Receive Image Data
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    start_time = time.time()

    # Read the image data (encoded JPEG bytes sent by the client)
    # Use raw bytes for the API
    image_file_bytes = request.files['image'].read()

    # 2. AZURE AI PROCESSING (Task 4.2)
    person_count = 0

    try:
        headers = {
            'Ocp-Apim-Subscription-Key': AZURE_VISION_KEY,
            # We send the raw image bytes in the request body
            'Content-Type': 'application/octet-stream'
        }

        # Send raw image bytes to Azure AI Vision API
        azure_response = requests.post(
            AZURE_VISION_URL, headers=headers, data=image_file_bytes, timeout=15)
        azure_response.raise_for_status()  # Raise error for bad status codes

        azure_result = azure_response.json()

        # --- Count People from Azure API Result (Detection Efficiency) ---
        if 'objects' in azure_result:
            for obj in azure_result['objects']:
                # The service detects various objects; we only care about 'person'
                if obj['object'].lower() == 'person':
                    person_count += 1

    except requests.exceptions.RequestException as e:
        print(f"Azure API Error: Could not connect or failed to process: {e}")
        # Log failure, continue with current iteration
        person_count = -1

    end_time = time.time()
    # Total time includes RTT to Azure AI service + Azure processing time + VM overhead
    process_duration = end_time - start_time

    # 3. Collect Performance Data (Task 4.3)
    cpu_util, mem_used, cost, bandwidth = get_performance_metrics(
        process_duration)

    current_datetime = datetime.now()
    log_vm_data(current_datetime, person_count, process_duration,
                cpu_util, mem_used, cost, bandwidth)

    print(f"[{current_datetime.strftime('%H:%M:%S')}] Azure AI Count: {person_count} (Time: {process_duration:.3f}s)")

    return jsonify({
        "status": "success",
        "people_count": person_count,
        # This is the total RTT from client.py to server.py to Azure and back
        "vm_processing_time_s": process_duration
    })


if __name__ == "__main__":
    if pd.io.common.file_exists(OUTPUT_CSV):
        import os
        os.remove(OUTPUT_CSV)

    app.run(host='0.0.0.0', port=5000)
