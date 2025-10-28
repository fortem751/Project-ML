import logging
import azure.functions as func
from ultralytics import YOLO
import cv2
import numpy as np
import json
import time

# =======================================================
# 1. V2 PROGRAMMING MODEL INITIALIZATION
# This top-level instance is CRUCIAL for the Python V2 worker to index your functions.
app = func.FunctionApp()
# =======================================================

# Load model globally for warm start efficiency
# This will run once when the worker starts up.
try:
    model = YOLO('yolov8n.pt')
    PERSON_CLASS_ID = 0
except Exception as e:
    logging.error(f"Failed to load YOLO model globally: {e}")
    # Consider what to do here: the function worker will likely fail to start if the model load fails.

# =======================================================
# 2. FUNCTION REGISTRATION
# The function is decorated to register it with the 'app' instance.


@app.route(route="imgproc1", auth_level=func.AuthLevel.ANONYMOUS)
def imgproc1(req: func.HttpRequest) -> func.HttpResponse:
    # =======================================================
    start_time = time.time()
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Check for image file in the request body
        image_bytes = req.get_body()
    except ValueError:
        return func.HttpResponse(
            "Please pass an image file in the request body",
            status_code=400
        )

    # Check if model failed to load globally, and return a 500 if so
    if 'model' not in globals():
        return func.HttpResponse("AI model not initialized. Check application logs for dependency errors.", status_code=500)

    # 1. Decode Image
    np_array = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    if frame is None:
        return func.HttpResponse("Invalid image format", status_code=400)

    # 2. Serverless AI Processing
    results = model(frame, verbose=False)

    person_count = 0
    for result in results:
        if result.boxes is not None:
            # Counts the number of detected objects whose class ID is PERSON_CLASS_ID (0)
            person_count += len([box for box in result.boxes.cls.cpu().tolist()
                                 if int(box) == PERSON_CLASS_ID])

    end_time = time.time()
    process_duration = end_time - start_time

    # 3. Performance Data (Monetary Cost & Efficiency)
    logging.info(
        f"Serverless Process Time: {process_duration:.3f}s, Count: {person_count}")

    # Return the result and response time
    return func.HttpResponse(
        json.dumps({
            "people_count": person_count,
            "response_time_s": process_duration
        }),
        mimetype="application/json",
        status_code=200
    )
