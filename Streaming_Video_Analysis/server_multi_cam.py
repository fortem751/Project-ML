from flask import Flask, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import time
import os  # Added for file existence check

app = Flask(__name__)
# Load the YOLOv8 Nano model once when the server starts
model = YOLO('yolov8n.pt')
PERSON_CLASS_ID = 0
# IMPORTANT: Use a new CSV name for multi-camera analysis
OUTPUT_CSV = "az_vm_results_multi.csv"


def get_performance_metrics(proc_time):
    """Simulated collection of VM resource metrics."""
    # Placeholder values for demonstration/initial logging
    cpu_util = np.random.uniform(50, 80)
    mem_used = np.random.uniform(200, 500)  # In MB
    bandwidth = np.random.uniform(500, 1000)  # In KB
    cost = proc_time * (0.0001 / 3600)  # Placeholder micro-cost
    return cpu_util, mem_used, cost, bandwidth


def log_vm_data(timestamp, count, proc_time, cpu_util, mem_used, cost, bandwidth, camera_id):
    """Logs results and performance metrics."""
    try:
        # NOTE: Using 'response_time_s' for consistency with analysis script
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

    image_file = request.files['image'].read()

    # Decode the JPEG bytes back into an OpenCV numpy array (the frame)
    np_array = np.frombuffer(image_file, np.uint8)
    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Invalid image format"}), 400

    # 2. VM AI Processing (YOLOv8)
    results = model(frame, verbose=False)

    person_count = 0  # Initialized here for safety
    for result in results:
        if result.boxes is not None:
            # Count boxes where the class ID matches 'person' (0)
            person_count += len([box for box in result.boxes.cls.cpu().tolist()
                                if int(box) == PERSON_CLASS_ID])

    end_time = time.time()
    process_duration = end_time - start_time

    # 3. Collect Performance Data
    cpu_util, mem_used, cost, bandwidth = get_performance_metrics(
        process_duration)

    current_datetime = datetime.now()

    # --- PATCH 3: Pass camera_id to logging function ---
    log_vm_data(current_datetime, person_count, process_duration,
                cpu_util, mem_used, cost, bandwidth, camera_id)

    print(f"[{current_datetime.strftime('%H:%M:%S')}] [{camera_id}] VM Detected: {person_count} (Time: {process_duration:.3f}s)")

    return jsonify({
        "status": "success",
        "people_count": person_count,
        "vm_processing_time_s": process_duration
    })


if __name__ == "__main__":
    if os.path.exists(OUTPUT_CSV):
        os.remove(OUTPUT_CSV)

    app.run(host='0.0.0.0', port=5000)
