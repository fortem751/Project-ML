import os
import cv2
import time
import pandas as pd
from ultralytics import YOLO
from datetime import datetime
import threading  # ADDED for multi-camera simulation
import numpy as np
from itertools import cycle

# --- CONFIGURATION (UPDATE THESE LINES) ---
# TASK 5: Define a list of sources to simulate multiple cameras
# List your video file multiple times, or use actual different URLs/files
WEBCAM_URLS = [
    r"London_cam.mp4",  # Camera 1
    r"Dublin.mp4",  # Camera 2
    r"NewYork.mp4",  # Camera 3
]
FRAME_INTERVAL_SECONDS = 5
# New CSV name for multi-camera local analysis
OUTPUT_CSV = "database_multi.csv"

# Load the YOLOv8 Nano model once when the script starts
# NOTE: In a true multi-threaded environment, having the model
# loaded globally might cause issues, but for basic concurrency, it often works.
model = YOLO('yolov8n.pt')
PERSON_CLASS_ID = 0


def log_data(timestamp, people_count, process_duration, camera_id):
    """Logs results and processing time, including the camera ID."""
    try:
        write_header = not os.path.exists(OUTPUT_CSV)

        # ADDED 'camera_id' column
        df = pd.DataFrame([{'timestamp': timestamp, 'people_count': people_count,
                            'response_time_s': process_duration, 'camera_id': camera_id}])

        df.to_csv(OUTPUT_CSV, mode='a', header=write_header, index=False)
    except Exception as e:
        print(f"[{camera_id}] Error logging data: {e}")


def process_frame_locally(frame):
    """Runs YOLOv8 on the frame and counts people."""
    # Run inference
    results = model(frame, verbose=False)

    person_count = 0
    for result in results:
        if result.boxes is not None:
            # Count boxes where the class ID matches 'person' (0)
            person_count += len([box for box in result.boxes.cls.cpu().tolist()
                                if int(box) == PERSON_CLASS_ID])

    return person_count


# --- PATCH: Refactored function for a single camera thread ---
def run_single_camera_stream(camera_id, camera_url):
    print(f"[{camera_id}] Starting local stream processing at: {camera_url}")

    cap = cv2.VideoCapture(camera_url)

    if not cap.isOpened():
        print(f"[{camera_id}] Error: Could not open video stream at {camera_url}")
        return

    while True:
        start_time = time.time()
        current_datetime = datetime.now()

        # 1. Capture Frame
        ret, frame = cap.read()

        if not ret:
            print(f"[{camera_id}] Error: Could not read frame. Restarting video.")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
            ret, frame = cap.read()

            if not ret:
                print(f"[{camera_id}] Failed to restart video. Stopping thread.")
                break

        # 2. Local AI Processing
        people_count = process_frame_locally(frame)

        end_time = time.time()
        process_duration = end_time - start_time

        print(f"[{current_datetime.strftime('%H:%M:%S')}] [{camera_id}] Detected: {people_count} (Time: {process_duration:.2f}s)")

        # 3. Data Logging
        log_data(current_datetime, people_count, process_duration, camera_id)

        # 4. Wait for the next interval
        time_to_wait = FRAME_INTERVAL_SECONDS - process_duration
        if time_to_wait > 0:
            time.sleep(time_to_wait)


def run_multi_camera_sls():
    threads = []
    print(f"Launching {len(WEBCAM_URLS)} local processing threads...")

    # Create and start a thread for each camera
    for i, url in enumerate(WEBCAM_URLS):
        camera_id = f"CAM_{i+1}"
        # Start a new thread for each stream
        thread = threading.Thread(
            target=run_single_camera_stream, args=(camera_id, url))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete (or for user interruption)
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\nLocal processing stopped by user.")


if __name__ == "__main__":
    # Ensure the CSV file starts fresh
    if os.path.exists(OUTPUT_CSV):
        os.remove(OUTPUT_CSV)

    run_multi_camera_sls()
