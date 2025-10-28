from flask import Flask, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import time
import uuid

app = Flask(__name__)
# Load the YOLOv8 Nano model (recommended for VM performance)
model = YOLO('yolov8n.pt') 

# Define COCO Class IDs
PERSON_CLASS_ID = 0
VEHICLE_CLASS_IDS = [2, 3, 5, 7]  # Car (2), Motorbike (3), Bus (5), Truck (7)

# Global dictionary to track unique person IDs observed by each camera.
# In a production environment, this state would live in a database (like Redis or Firestore).
# Format: {'camera_id_1': {'track_id_A', 'track_id_B', ...}, 'camera_id_2': {...}}
unique_person_tracker = {}

OUTPUT_CSV = "az_vm_results_advanced.csv"

# --- Placeholder for VM Performance Metrics (Same as previous server) ---
def get_performance_metrics(proc_time):
    """Simulated collection of VM resource metrics."""
    # Placeholder values for demonstration/initial logging
    cpu_util = np.random.uniform(50, 80) 
    mem_used = np.random.uniform(200, 500) # In MB
    bandwidth = np.random.uniform(500, 1000) # In KB
    cost = proc_time * (0.0001 / 3600) # Placeholder micro-cost
    return cpu_util, mem_used, cost, bandwidth

def log_vm_data(timestamp, camera_id, people_count, vehicle_count, unique_person_count, proc_time, cpu_util, mem_used, cost, bandwidth):
    """Logs results and performance metrics, now including vehicle and unique counts."""
    try:
        write_header = not pd.io.common.file_exists(OUTPUT_CSV)
        
        df = pd.DataFrame([{'timestamp': timestamp, 'camera_id': camera_id, 
                            'people_count': people_count, 'vehicle_count': vehicle_count,
                            'unique_person_count': unique_person_count,
                            'proc_time_s': proc_time, 'cpu_util_%': cpu_util,
                            'mem_used_MB': mem_used, 'cost_usd': cost, 
                            'bandwidth_KB': bandwidth}])
        
        df.to_csv(OUTPUT_CSV, mode='a', header=write_header, index=False)
    except Exception as e:
        print(f"Error writing to CSV: {e}")

@app.route('/process_frame', methods=['POST'])
def process_frame():
    start_time = time.time()
    
    # 1. Image and Metadata Retrieval
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400

    image_file = request.files['image'].read()
    # Safely retrieve camera_id from form data, defaulting to a UUID if not provided
    camera_id = request.form.get('camera_id', f'CAM_{str(uuid.uuid4())[:8]}') 
    
    # Reconstruct the JPEG bytes back into an OpenCV numpy array (the frame)
    np_array = np.frombuffer(image_file, np.uint8)
    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Invalid image format"}), 400

    # 2. VM AI Processing with Tracking
    # Use the 'tracker' argument to enable object tracking
    results = model.track(frame, persist=True, verbose=False) 
    
    people_count = 0
    vehicle_count = 0
    
    # Initialize the camera's unique tracker set if it doesn't exist
    if camera_id not in unique_person_tracker:
        unique_person_tracker[camera_id] = set()

    for result in results:
        # Check if tracking IDs are available
        if result.boxes is not None and result.boxes.id is not None:
            
            track_ids = result.boxes.id.cpu().tolist()
            class_ids = result.boxes.cls.cpu().tolist()

            for track_id, cls_id in zip(track_ids, class_ids):
                # Classify the object
                if int(cls_id) == PERSON_CLASS_ID:
                    people_count += 1
                    # Add the track ID to the set for unique counting
                    unique_person_tracker[camera_id].add(int(track_id))
                elif int(cls_id) in VEHICLE_CLASS_IDS:
                    vehicle_count += 1
            
    # Calculate unique count for logging
    unique_person_count = len(unique_person_tracker[camera_id])
            
    end_time = time.time()
    process_duration = end_time - start_time
    
    # 3. Collect Performance Data
    cpu_util, mem_used, cost, bandwidth = get_performance_metrics(process_duration)

    current_datetime = datetime.now()
    log_vm_data(current_datetime, camera_id, people_count, vehicle_count, unique_person_count, 
                process_duration, cpu_util, mem_used, cost, bandwidth)

    print(f"[{current_datetime.strftime('%H:%M:%S')}] {camera_id} -> People: {people_count}, Vehicles: {vehicle_count}, Unique People: {unique_person_count} (Time: {process_duration:.3f}s)")

    return jsonify({
        "status": "success",
        "camera_id": camera_id,
        "people_count": people_count,
        "vehicle_count": vehicle_count,
        "unique_person_count": unique_person_count,
        "vm_processing_time_s": process_duration
    })

if __name__ == "__main__":
    # Ensure CSV starts fresh for new run
    if os.path.exists(OUTPUT_CSV):
        os.remove(OUTPUT_CSV)
    print("VM Server Started: Listening for frames with tracking enabled.")
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
