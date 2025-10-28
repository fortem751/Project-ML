import cv2
import time
import requests
from io import BytesIO
from datetime import datetime
import numpy as np
import threading  # ADDED for multi-camera simulation
import os
from itertools import cycle  # ADDED to endlessly cycle the video file


# TASK 5: Define a list of sources to simulate multiple cameras

WEBCAM_URLS = [
    r"London_cam.mp4",  # Camera 1
    r"Dublin.mp4",  # Camera 2
    r"NewYork.mp4",  # Camera 3
]

# Use the API_ENDPOINT for the specific experiment you are running (Part 2 or Part 4)
# Example Part 2 (VM YOLO):
VM_PUBLIC_IP = "AZURE_VM_PUBLIC_IP"
API_ENDPOINT = f"http://{VM_PUBLIC_IP}:5000/process_frame"
# Example Part 4 (Azure AI Service on VM):
# API_ENDPOINT = "http://YOUR_VM_IP:5000/process_frame"

FRAME_INTERVAL_SECONDS = 5
CONNECTION_TIMEOUT = 20  # Timeout for each request


# Refactored to handle a single camera stream
def process_single_camera_stream(camera_id, camera_url):
    print(f"[{camera_id}] Starting stream. Sending frames to: {API_ENDPOINT}")

    # Use the cycle utility to loop video if using a local file
    if os.path.exists(camera_url):
        # We need a new VideoCapture object for each thread
        cap = cv2.VideoCapture(camera_url)
    else:
        # If using a live URL, use it directly
        cap = cv2.VideoCapture(camera_url)

    if not cap.isOpened():
        print(f"[{camera_id}] Error: Could not open video stream at {camera_url}")
        return

    while True:
        start_time_total = time.time()  # Start RTT timer

        # 1. Capture Frame
        ret, frame = cap.read()

        if not ret:
            print(f"[{camera_id}] Error: Could not read frame. Restarting video.")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
            ret, frame = cap.read()  # Read the first frame after loop

            if not ret:
                print(
                    f"[{camera_id}] Error: Failed to restart video. Stopping thread.")
                break

        # 2. Encode Frame
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        _, img_encoded = cv2.imencode('.jpg', frame, encode_param)

        # 3. Send to VM
        try:
            response = requests.post(
                API_ENDPOINT,
                files={
                    'image': (f'frame_{camera_id}.jpg', BytesIO(img_encoded.tobytes()), 'image/jpeg')
                },
                # *** PATCH: Send camera_id as form data ***
                data={'camera_id': camera_id},
                timeout=CONNECTION_TIMEOUT
            )
            response.raise_for_status()

            result = response.json()
            people_count = result.get("people_count", "N/A")

            end_time_total = time.time()
            response_time_rtt = end_time_total - start_time_total

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{camera_id}] Count: {people_count} (Total RTT: {response_time_rtt:.3f}s)")

        except requests.exceptions.RequestException as e:
            print(f"[{camera_id}] Error connecting or during request: {e}")

        # 4. Wait for the next interval
        time_to_wait = FRAME_INTERVAL_SECONDS - \
            (time.time() - start_time_total)
        if time_to_wait > 0:
            time.sleep(time_to_wait)


def run_multi_camera_sls_client():
    threads = []
    print(f"Launching {len(WEBCAM_URLS)} camera threads...")

    # Create and start a thread for each camera
    for i, url in enumerate(WEBCAM_URLS):
        camera_id = f"CAM_{i+1}"
        thread = threading.Thread(
            target=process_single_camera_stream, args=(camera_id, url))
        threads.append(thread)
        thread.start()

    # Keep the main thread alive until user interruption
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\nClient stopped by user. Waiting for threads to terminate...")


if __name__ == "__main__":
    run_multi_camera_sls_client()
