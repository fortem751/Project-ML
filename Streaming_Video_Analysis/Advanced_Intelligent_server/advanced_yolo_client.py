import cv2
import time
import requests
from io import BytesIO
from datetime import datetime
import numpy as np  # Needed for imencode
import threading
import uuid
import os # For checking if video file exists

# --- CONFIGURATION (UPDATE THESE LINES) ---
# Use a local video file for robust testing
WEBCAM_URL = "London_cam.mp4" 
VM_PUBLIC_IP = "172.161.111.26"  # Replace with your Azure VM IP
FRAME_INTERVAL_SECONDS = 5
API_ENDPOINT = f"http://{VM_PUBLIC_IP}:5000/process_frame"

# --- ADVANCED OPTIMIZATION CONFIG ---
# 7.2.1 Dynamic Resolution Adjustment: Target resolution for frame *sent* to VM
TARGET_WIDTH = 640
TARGET_HEIGHT = 360 

# 7.2.2 Motion Detection on the Edge: Threshold for minimum detected motion area (pixels)
MOTION_THRESHOLD_AREA = 5000 
# 7.2.3 Advanced Image Compression: JPEG quality (0-100). Lower is smaller file size.
JPEG_QUALITY = 75

# Initialize motion detector outside the loop to maintain background state
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

def detect_motion(frame):
    """
    Performs motion detection on the frame using Background Subtraction (MOG2).
    Returns True if motion above MOTION_THRESHOLD_AREA is detected.
    """
    # 1. Apply background subtractor
    fgmask = fgbg.apply(frame)

    # 2. Threshold the mask (removes shadows and small noise)
    # Binary threshold: pixels must be completely foreground (255)
    _, thresh = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY) 

    # 3. Find contours (regions of motion)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 4. Check for significant motion
    total_motion_area = 0
    for contour in contours:
        # Filter out small contours (noise)
        if cv2.contourArea(contour) > 500:
            total_motion_area += cv2.contourArea(contour)
            
    # Check if total motion area exceeds the defined threshold
    if total_motion_area > MOTION_THRESHOLD_AREA:
        return True
    
    return False


def process_stream(camera_id, webcam_url):
    """Handles stream capture, edge processing, and conditional cloud transmission."""
    print(f"[{camera_id}] Starting stream client. Target: {API_ENDPOINT}")
    cap = cv2.VideoCapture(webcam_url)

    if not cap.isOpened():
        print(f"[{camera_id}] Error: Could not open video stream at {webcam_url}.")
        return

    while True:
        start_time_total = time.time()  # Start RTT timer
        
        # 1. Capture Frame
        ret, frame = cap.read()
        if not ret:
            # Handle video end/stream disconnect (rewind local file)
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            time.sleep(1) 
            continue

        original_width = frame.shape[1]
        original_height = frame.shape[0]

        # 2. Edge Optimization: Dynamic Resolution Adjustment (7.2.1)
        if TARGET_WIDTH != original_width or TARGET_HEIGHT != original_height:
            frame_resized = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT))
        else:
            frame_resized = frame

        # 3. Edge Optimization: Motion Detection (7.2.2)
        if not detect_motion(frame_resized):
            print(f"[{camera_id}] No significant motion detected. Skipping API call.")
            time_to_wait = FRAME_INTERVAL_SECONDS - (time.time() - start_time_total)
            if time_to_wait > 0:
                time.sleep(time_to_wait)
            continue # Skip the rest of the loop (no API call)

        # 4. Image Encoding with Advanced Compression (7.2.3)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        _, img_encoded = cv2.imencode('.jpg', frame_resized, encode_param)

        # 5. Send to VM (Only if motion was detected)
        try:
            response = requests.post(
                API_ENDPOINT,
                # Send the camera ID in the form data
                files={'image': ('frame.jpg', BytesIO(img_encoded.tobytes()), 'image/jpeg')},
                data={'camera_id': camera_id},
                timeout=20  
            )
            response.raise_for_status() 

            result = response.json()
            people_count = result.get("people_count", "N/A")
            vehicle_count = result.get("vehicle_count", "N/A")
            unique_person_count = result.get("unique_person_count", "N/A")

            end_time_total = time.time()
            response_time_rtt = end_time_total - start_time_total 
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{camera_id}] MOTION! Ppl: {people_count} (Unique: {unique_person_count}), Veh: {vehicle_count} (RTT: {response_time_rtt:.3f}s)")

        except requests.exceptions.RequestException as e:
            print(f"[{camera_id}] Error connecting to VM or during request: {e}")

        # 6. Wait for the next interval
        time_to_wait = FRAME_INTERVAL_SECONDS - (time.time() - start_time_total)
        if time_to_wait > 0:
            time.sleep(time_to_wait)


if __name__ == "__main__":
    
    # Simulate a multi-camera setup using multiple threads
    # NOTE: You need multiple copies of the video file or a single RTSP/MJPEG stream to test concurrency effectively.
    camera_sources = [
        {'id': 'CAM_A', 'url': WEBCAM_URL}, # Use the same video for local testing
        {'id': 'CAM_B', 'url': WEBCAM_URL},
        {'id': 'CAM_C', 'url': WEBCAM_URL},
        {'id': 'CAM_D', 'url': WEBCAM_URL}
    ]
    
    threads = []
    for source in camera_sources:
        thread = threading.Thread(target=process_stream, args=(source['id'], source['url']))
        threads.append(thread)
        thread.start()
        # Stagger the start of each thread to simulate real-world arrival times
        time.sleep(0.5) 
        
    for thread in threads:
        thread.join()
    
    print("All streams finished processing.")
