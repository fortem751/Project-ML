from flask import Flask, request, jsonify
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import time
import requests
import os

app = Flask(__name__)
# No local YOLO model is loaded here
OUTPUT_CSV = "az_ai_results_multi.csv"  # IMPORTANT: New CSV name for Task 5

# --- AZURE CONFIGURATION (Task 4.1 Output) ---
# IMPORTANT: REPLACE THESE PLACEHOLDERS
AZURE_VISION_ENDPOINT = "https://azimgprocessing1.cognitiveservices.azure.com/"
AZURE_VISION_KEY = "AZURE_VISION_KEY"
AZURE_VISION_URL = f"{AZURE_VISION_ENDPOINT}/vision/v3.2/analyze?visualFeatures=Tags,Objects&language=en"


def get_performance_metrics(proc_time):
    """Simulated collection of VM resource metrics. Lower CPU expected here."""
    cpu_util = np.random.uniform(10, 30)
    mem_used = np.random.uniform(100, 200)
    bandwidth = np.random.uniform(500, 1000)
    cost = proc_time * (0.0001 / 3600)
    return cpu_util, mem_used, cost, bandwidth


def log_vm_data(timestamp, count, proc_time, cpu_util, mem_used, cost, bandwidth, camera_id):
    """Logs results and performance metrics."""
    try:
        write_header = not os.path.exists(OUTPUT_CSV)

        # ADDED 'camera_id' to the DataFrame
        df = pd.DataFrame([{'timestamp': timestamp, 'people_count': count, 'response_time_s': proc_time,
                            'cpu_util_%': cpu_util, 'mem_used_mb': mem_used,
                            'cost_unit': cost, 'bandwidth_kb': bandwidth, 'camera_id': camera_id}])
        df.to_csv(OUTPUT_CSV, mode='a', header=write_header, index=False)
    except Exception as e:
        print(f"Error logging data on VM: {e}")


@app.route('/process_frame', methods=['POST'])
def process_frame():
    # 1. Receive Image Data
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    # --- PATCH 2: Get camera_id from form data ---
    camera_id = request.form.get('camera_id', 'UNKNOWN_CAM')

    start_time = time.time()

    # *** FIX: Initialize person_count outside the try block ***
    person_count = 0

    image_file_bytes = request.files['image'].read()

    # 2. AZURE AI PROCESSING
    try:
        headers = {
            'Ocp-Apim-Subscription-Key': AZURE_VISION_KEY,
            'Content-Type': 'application/octet-stream'
        }

        azure_response = requests.post(
            AZURE_VISION_URL, headers=headers, data=image_file_bytes, timeout=15)
        azure_response.raise_for_status()

        azure_result = azure_response.json()

        # --- Count People from Azure API Result ---
        if 'objects' in azure_result:
            for obj in azure_result['objects']:
                # The service detects various objects; we only care about 'person'
                if obj['object'].lower() == 'person':
                    person_count += 1

    except requests.exceptions.RequestException as e:
        print(f"Azure API Error: Could not connect or failed to process: {e}")
        # Log a failure count
        person_count = -1

    end_time = time.time()
    process_duration = end_time - start_time

    # 3. Collect Performance Data
    cpu_util, mem_used, cost, bandwidth = get_performance_metrics(
        process_duration)

    current_datetime = datetime.now()

    # --- PATCH 3: Pass camera_id to logging function ---
    log_vm_data(current_datetime, person_count, process_duration,
                cpu_util, mem_used, cost, bandwidth, camera_id)

    print(f"[{current_datetime.strftime('%H:%M:%S')}] [{camera_id}] Azure AI Count: {person_count} (Time: {process_duration:.3f}s)")

    return jsonify({
        "status": "success",
        "people_count": person_count,
        "vm_processing_time_s": process_duration
    })


if __name__ == "__main__":
    if os.path.exists(OUTPUT_CSV):
        os.remove(OUTPUT_CSV)

    app.run(host='0.0.0.0', port=5000)
