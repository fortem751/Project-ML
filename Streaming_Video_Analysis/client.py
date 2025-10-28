import cv2
import time
import requests
from io import BytesIO
from datetime import datetime
import numpy as np  # Needed for imencode

# --- CONFIGURATION (UPDATE THESE LINES) ---
# Use the URL that worked for you
WEBCAM_URL = "London_cam.mp4"
VM_PUBLIC_IP = "AZURE_VM_PUBLIC_IP"  # Get this from Azure Portal
FRAME_INTERVAL_SECONDS = 5
API_ENDPOINT = f"http://{VM_PUBLIC_IP}:5000/process_frame"


def run_vm_sls_client():
    print(f"Starting SLS VM Client. Sending frames to: {API_ENDPOINT}")
    cap = cv2.VideoCapture(WEBCAM_URL)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        start_time_total = time.time()  # Start RTT timer

        # 1. Capture Frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame. Retrying...")
            cap.release()
            time.sleep(FRAME_INTERVAL_SECONDS)
            cap = cv2.VideoCapture(WEBCAM_URL)
            continue

        # 2. Encode frame for transmission (creates the 'img_encoded' variable)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        # img_encoded holds the raw binary data (bytes)
        _, img_encoded = cv2.imencode('.jpg', frame, encode_param)

        # 3. Send to VM
        try:
            # We use BytesIO to wrap the binary data in a file-like object for the POST request
            response = requests.post(
                API_ENDPOINT,
                # .tobytes() converts the numpy array containing JPEG data into raw bytes
                files={'image': ('frame.jpg', BytesIO(
                    img_encoded.tobytes()), 'image/jpeg')},
                timeout=20  # Allow sufficient time for network latency + processing
            )
            response.raise_for_status()  # Raise exception for bad status codes (4xx or 5xx)

            result = response.json()
            people_count = result.get("people_count", "N/A")

            end_time_total = time.time()
            response_time_rtt = end_time_total - \
                start_time_total  # Total Round Trip Time (RTT)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] VM Count: {people_count} (Total RTT: {response_time_rtt:.3f}s)")

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to VM or during request: {e}")

        # 4. Wait for the next interval
        time_to_wait = FRAME_INTERVAL_SECONDS - \
            (time.time() - start_time_total)
        if time_to_wait > 0:
            time.sleep(time_to_wait)


if __name__ == "__main__":
    try:
        run_vm_sls_client()
    except KeyboardInterrupt:
        print("\nSLS VM Client stopped by user.")
