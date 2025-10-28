import os
import cv2
import time
import pandas as pd
from ultralytics import YOLO
from datetime import datetime
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
# Replace with your actual URL (e.g., RTSP, MJPEG)
# WEBCAM_URL = "http://87.75.106.150:8080/mjpg/video.mjpg"
WEBCAM_URL = "London_cam.mp4"
FRAME_INTERVAL_SECONDS = 5
OUTPUT_CSV = "database.csv"

# Load the YOLOv8 Nano model (small and fast)
model = YOLO('yolov8n.pt')

# Define the class ID for 'person' in COCO dataset (usually 0)
PERSON_CLASS_ID = 0


def process_frame_locally(frame):
    """Runs YOLOv8 on the frame and counts people."""
    # Run inference
    results = model(frame, verbose=False)

    # Extract bounding boxes and filter for people
    person_count = 0

    # Iterate through detection results
    for result in results:
        # Check if the result has detections
        if result.boxes is not None:
            # Count boxes where the class ID matches 'person' (0)
            # .cpu() ensures tensors are on the CPU for list conversion
            # .tolist() converts PyTorch tensor to Python list
            person_count += len([box for box in result.boxes.cls.cpu().tolist()
                                if int(box) == PERSON_CLASS_ID])

    return person_count


# --- PATCH: Added 'duration' parameter and 'response_time_s' column ---
def log_data(timestamp, count, duration):
    """Appends the result to a CSV file, ensuring the header is written if the file is new."""
    try:
        # 1. Check if the file exists using the standard os library
        write_header = not os.path.exists(OUTPUT_CSV)

        df = pd.DataFrame(
            [{'timestamp': timestamp, 'people_count': count, 'response_time_s': duration}])

        # 2. Append to CSV. header=True only if the file did not exist (write_header is True).
        df.to_csv(OUTPUT_CSV, mode='a', header=write_header, index=False)

    except Exception as e:
        print(f"CRITICAL ERROR logging data locally: {e}")


def run_local_sls():
    """Main function to run the local Smart Lighting System."""
    print(f"Starting SLS Local Processor. Capturing from: {WEBCAM_URL}")
    cap = cv2.VideoCapture(WEBCAM_URL)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        start_time = time.time()

        # 1. Capture Frame (Task 1.2)
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame. Retrying...")
            cap.release()
            time.sleep(FRAME_INTERVAL_SECONDS)
            cap = cv2.VideoCapture(WEBCAM_URL)
            continue

        current_datetime = datetime.now()

        # 1. Encode frame for transmission/storage (e.g., as JPEG bytes)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        # This function stores the encoded binary data (bytes) in the 'img_encoded' variable.
        # 'img_encoded' is the "processed frame" data you can send.
        _, img_encoded = cv2.imencode('.jpg', frame, encode_param)

        # 2. Local AI Processing (Task 1.3)
        people_count = process_frame_locally(frame)

        end_time = time.time()
        process_duration = end_time - start_time

        print(f"[{current_datetime.strftime('%Y-%m-%d %H:%M:%S')}] People Detected: {people_count} (Processing Time: {process_duration:.2f}s)")

        # 3. Data Logging
        # --- PATCH: Pass duration to log_data ---
        log_data(current_datetime, people_count, process_duration)

        # Save a processed frame every iteration for review
        cv2.imwrite('processed_frame.jpg', frame)

        # 4. Wait for the next interval
        time_to_wait = FRAME_INTERVAL_SECONDS - process_duration
        if time_to_wait > 0:
            time.sleep(time_to_wait)


if __name__ == "__main__":
    # Ensure the CSV file starts fresh if running multiple times (using os.path.exists for consistency)
    if os.path.exists(OUTPUT_CSV):
        print(f"Removing existing {OUTPUT_CSV}")
        os.remove(OUTPUT_CSV)

    # Run the system (Press Ctrl+C to stop)
    try:
        run_local_sls()
    except KeyboardInterrupt:
        print("\nSLS Local Processor stopped by user.")
