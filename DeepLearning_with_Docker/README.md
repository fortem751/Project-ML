# DL Inference Deployment with Docker (USing Docker Compose as orchestrator).

This repository contains a complete solution for deploying a Deep Learning inference service and its graphical interface in separate Docker containers, orchestrated using Docker Compose.

## Features

- Two-Tier Architecture: Complete logical separation between the model inference (FastAPI) and the user interface (Gradio).

- Deep Learning Backend: Uses PyTorch and a pre-trained ResNet18 for image classification inference.

- Container Optimization: Dockerfiles are structured to leverage the build cache and use a slim base image to reduce final image size.

- GPU Ready: Configuration is included to enable NVIDIA GPU acceleration via the NVIDIA Container Toolkit for maximum performance.

## Prerequisites

- Docker Engine: Must be installed and running on your system (compatible with Linux, MacOS, and Windows).

- Docker Compose: Typically bundled with recent Docker Desktop installations.

**GPU Deployment Only**:

- A host machine with a NVIDIA GPU.

- The NVIDIA Container Toolkit must be installed and configured.

## Project Structure

**app_api/**                      # Inference Container (FastAPI + PyTorch).
- api.py                    # FastAPI server exposing the /predict/ endpoint.
- Dockerfile.api            # Docker build instructions.
- requirements_api.txt      # Python dependencies (torch, fastapi, python-multipart, etc.).
**app_gui/**                      # GUI Container (Gradio).
- gui.py                    # Gradio frontend that calls the API container.
- Dockerfile.gui            # Docker build instructions.
- requirements_gui.txt      # Python dependencies (gradio, requests).
- docker-compose.yml            # Orchestration file defining both services.

## Setup and Execution
1. **Clone the Repository**.

- git clone https://github.com/fortem751/Project-ML.git:
- cd DeepLearning_with_Docker:

2. **Run the Application**.
The command below builds the images and starts both the api and gui containers in detached mode (-d).

- docker compose up -d --build # This command uses the docker-compose.yml file to orchestrate the build and run

Note on GPU: The docker-compose.yml is configured to use the runtime: nvidia option, along with parameters like shm_size: '2gb', to utilize the GPU if the NVIDIA Container Toolkit is available on the host.

3. **Verification and Access** :Confirm both services are running.

- docker ps

- http://localhost:8080 # Access the GUI: Open your web browser to the mapped port. The GUI container (running Gradio on port 7860) is accessible on your host via port 8080.

**Cleanup** : To stop and remove all containers and the network created by Docker Compose:

- docker compose down