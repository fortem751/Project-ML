DL Inference Deployment with Docker Compose
This repository contains a solution for deploying a Deep Learning inference service and its graphical interface in separate Docker containers. This setup uses FastAPI for the backend model serving and Gradio for the simple web interface.
Prerequisites
Docker Engine & Docker Compose: Installed and running.
GPU Setup (Optional): Requires a host machine with an NVIDIA GPU and the NVIDIA Container Toolkit installed.
Project Structure
.
├── app_api/                      # Inference Container (FastAPI + PyTorch)
│   ├── api.py                    
│   ├── Dockerfile.api            
│   └── requirements_api.txt      
├── app_gui/                      # GUI Container (Gradio)
│   ├── gui.py                    
│   ├── Dockerfile.gui            
│   └── requirements_gui.txt      
└── docker-compose.yml            # Orchestration

Setup and Execution
Clone the Repository
Bash
git clone [YOUR-REPO-URL]
cd [YOUR-REPO-NAME]


Build and Run the Services
The command below builds both images and starts the two containers (api and gui) in detached mode (-d). The included configuration is GPU-ready.
Bash
# This command uses the docker-compose.yml file to orchestrate the build and run
docker compose up -d --build


Access the Application
Once the containers are running, access the application GUI via your web browser:
http://localhost:8080


Container Details
Service Name
Role
Technology
Exposed Port (Host)
api
Deep Learning Inference
FastAPI + PyTorch
Internal (8000)
gui
Graphical User Interface
Gradio
8080

Cleanup
To stop and remove all containers and the network created by Docker Compose:
Bash
docker compose down

