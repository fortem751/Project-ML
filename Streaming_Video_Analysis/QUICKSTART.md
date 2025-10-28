# Quick Start Guide

Get up and running with Smart Video Stream Analysis System in 5 minutes!

## 🚀 Fastest Path to Success

### Option 1: Local Processing (Easiest)

Perfect for testing without any cloud setup:

```bash
# 1. Clone and install
git clone https://github.com/fortem751/Project-ML.git
cd smart-streaming-analysis
pip install ultralytics opencv-python pandas numpy matplotlib

# 2. Run local processing
python fetch_stream.py
```

**That's it!** The system will:
- Download YOLOv8 model automatically (first run only)
- Process the default video file
- Save results to `database.csv`
- Print detection results to console

### Option 2: Cloud VM Processing

For distributed processing:

```bash
# 1. Deploy on Azure VM
# (Create a VM in Azure Portal first)
ssh your-vm-username@your-vm-ip
git https://github.com/fortem751/Project-ML.git
cd smart-streaming-analysis
pip install -r requirements.txt
python server.py

# 2. Run client on local machine
# Edit client.py and set VM_PUBLIC_IP to your Azure VM IP
python client.py
```

### Option 3: Azure AI Services

For managed AI processing:

```bash
# 1. Create Azure Computer Vision resource
# (Use Azure Portal: Create > AI + Machine Learning > Computer Vision)

# 2. Configure credentials
cp .env.example .env
# Edit .env with your Azure credentials

# 3. Run AI server
python ai_server.py

# 4. Run client
python client.py
```

### Option 4: 🚀 Advanced Edge-Optimized (Recommended)

Best performance with cost optimization:

```bash
# 1. Deploy on Azure VM
ssh your-vm-username@your-vm-ip
git clone https://github.com/fortem751/Project-ML.git
cd smart-streaming-analysis
pip install -r requirements.txt
python advanced_yolo_server.py

# 2. Run advanced client on local machine
# Edit advanced_yolo_client.py and set VM_PUBLIC_IP
python advanced_yolo_client.py
```

**Benefits**:
- 70% fewer API calls via motion detection
- 88% less bandwidth with resolution optimization
- Vehicle detection included
- Unique visitor tracking
- Multi-camera support out of the box

## 📝 Basic Configuration

### Update Video Source

Edit the Python file you're using:

```python
# For local video file
WEBCAM_URL = "your_video.mp4"

# For RTSP stream
WEBCAM_URL = "rtsp://username:password@camera_ip:554/stream"

# For webcam
WEBCAM_URL = 0  # Default camera
```

### Adjust Processing Interval

```python
FRAME_INTERVAL_SECONDS = 5  # Process every 5 seconds
```

### Advanced Configuration (for advanced_yolo_client.py)

Quick tuning for optimal performance:

```python
# Reduce bandwidth (recommended for cellular/slow connections)
TARGET_WIDTH = 640
TARGET_HEIGHT = 360
JPEG_QUALITY = 70  # Lower quality = less bandwidth

# Adjust motion sensitivity
MOTION_THRESHOLD_AREA = 5000  # Lower = more sensitive
                               # Higher = fewer API calls

# Multi-camera setup
camera_sources = [
    {'id': 'FRONT_DOOR', 'url': 'rtsp://camera1_url'},
    {'id': 'BACK_DOOR', 'url': 'rtsp://camera2_url'}
]
```

## 📊 View Results

After running, check the generated CSV files:

```bash
# Local processing results
cat database.csv

# VM processing results
cat az_vm_results.csv

# Run analysis
python per_analysis_local.py
```

Results include:
- Timestamp of detection
- Number of people detected
- Processing time
- Resource utilization metrics

## 🎯 Common Use Cases

### Use Case 1: Test Different Architectures

```bash
# Compare all methods with same video source:
python fetch_stream.py          # Local (baseline)
python client.py                # Cloud VM
# (Configure and use ai_server.py for Azure AI)

# Then analyze
python per_analysis_local.py
```

### Use Case 2: Monitor Multiple Cameras

```bash
# Server side
python server_multi_cam.py

# Client side
python client_multi_cameras.py
```

### Use Case 3: Real-time Monitoring

```bash
# Use live camera feed
WEBCAM_URL = 0  # Or RTSP URL
FRAME_INTERVAL_SECONDS = 1  # Process every second
```

## 🔧 Troubleshooting Quick Fixes

### Problem: "Could not open video stream"
```bash
# Solution: Check video file path or camera connection
ls -la London_cam.mp4  # Verify file exists
```

### Problem: "Module not found"
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt
```

### Problem: "Connection refused" (cloud VM)
```bash
# Solution: Check Azure NSG rules
# Ensure port 5000 is open in Azure Network Security Group
```

### Problem: Slow processing
```bash
# Solution: Increase frame interval
FRAME_INTERVAL_SECONDS = 10  # Process less frequently
```

## ⚡ Deployment Tips

1. **Start simple**: Begin with local processing before moving to cloud
2. **Test with short videos**: Use 30-60 second clips for initial testing
3. **Monitor resources**: Keep an eye on CPU/memory during processing
4. **Gradual scaling**: Test single camera before multi-camera setup
5. **Check logs**: Console output provides real-time status updates

---

