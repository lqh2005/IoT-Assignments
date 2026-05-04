# 🚀 Assignment 17: Run Other Services on the Edge

Deploy Azure Functions as Docker containers to IoT Edge devices for local processing.

## 🎯 Quick Start

### 1. Install Docker

Download and install Docker Desktop:
- **Windows/Mac**: https://www.docker.com/products/docker-desktop
- **Linux**: `curl https://get.docker.com | sh`

### 2. Build Container Image

```bash
cd Assignment_17

# Build image
docker build -t fruitclassifier:latest .

# Verify image was created
docker images | grep fruitclassifier
```

### 3. Test Locally

#### Option A: Windows PowerShell

```powershell
.\setup_edge.ps1
```

#### Option B: Linux/Mac Bash

```bash
chmod +x setup_edge.sh
./setup_edge.sh
```

#### Option C: Manual Testing

```bash
# Start container
docker run -d --name test-fruit -p 8000:8000 fruitclassifier:latest

# Test health check
curl http://localhost:8000/health

# Test classification
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "fruit_type": "apple",
    "device_id": "test-device"
  }'

# View container logs
docker logs test-fruit

# Get statistics
curl http://localhost:8000/stats

# Stop container
docker stop test-fruit
docker rm test-fruit
```

## 📁 File Structure

```
Assignment_17/
├── Dockerfile                 # Container definition
├── function_app.py            # Flask HTTP server + endpoints
├── route_handler.py           # Business logic (classification, events)
├── deployment.json            # IoT Edge deployment manifest
├── requirements.txt           # Python package dependencies
├── setup_edge.sh              # Linux/Mac setup script
├── setup_edge.ps1             # Windows setup script
├── assignment17.md            # Detailed documentation
└── README.md                  # This file
```

## 🔌 HTTP API Endpoints

### 1. Health Check

```bash
GET http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "uptime": "0:00:23.456789",
  "messages_processed": 5
}
```

### 2. Classify Image

```bash
POST http://localhost:8000/classify
Content-Type: application/json

{
  "image_data": "base64_encoded_image_here",
  "fruit_type": "apple",
  "device_id": "camera-01"
}
```

**Response**:
```json
{
  "success": true,
  "device_id": "camera-01",
  "fruit_type": "apple",
  "prediction": "ripe",
  "confidence": 0.92,
  "location": "edge",
  "processed_at": "2026-05-04T10:30:45.123456",
  "message": "Image classified as ripe on edge device"
}
```

### 3. Process IoT Event

```bash
POST http://localhost:8000/process-iot-event
Content-Type: application/json

{
  "device_id": "sensor-01",
  "sensor_data": {
    "temperature": 22.5,
    "humidity": 65,
    "ripeness": "ripe"
  },
  "timestamp": "2026-05-04T10:30:45Z"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Event processed on edge device",
  "processed_event": {
    "device_id": "sensor-01",
    "processing_location": "edge",
    "status": "processed"
  }
}
```

### 4. Store Data (Local Blob Storage)

```bash
POST http://localhost:8000/store-blob
Content-Type: application/json

{
  "filename": "sensor_data_2026-05-04.json",
  "data": {
    "temperature": 22.5,
    "ripeness": "ripe"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Data stored to edge_storage/sensor_data_2026-05-04.json",
  "filepath": "edge_storage/sensor_data_2026-05-04.json"
}
```

### 5. Get Statistics

```bash
GET http://localhost:8000/stats
```

**Response**:
```json
{
  "statistics": {
    "total_requests": 15,
    "successful_processing": 12,
    "errors": 0,
    "start_time": "2026-05-04T10:25:30.123456",
    "messages_processed": 3
  },
  "current_time": "2026-05-04T10:30:45.123456"
}
```

## 🐳 Docker Commands

### Build Image

```bash
# Build with tag
docker build -t fruitclassifier:latest .

# Build with custom name and version
docker build -t myregistry.azurecr.io/fruitclassifier:v1.0 .
```

### Run Container

```bash
# Interactive mode (foreground)
docker run -p 8000:8000 fruitclassifier:latest

# Detached mode (background)
docker run -d --name myfruit -p 8000:8000 fruitclassifier:latest

# With volume mounting (persist data)
docker run -d --name myfruit \
  -p 8000:8000 \
  -v $(pwd)/edge_storage:/app/edge_storage \
  fruitclassifier:latest

# With environment variables
docker run -d --name myfruit \
  -p 8000:8000 \
  -e DEVICE_ID="edge-01" \
  fruitclassifier:latest
```

### Manage Container

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View logs
docker logs myfruit

# Follow logs (tail -f)
docker logs -f myfruit

# Execute command in container
docker exec myfruit ls -la

# Stop container
docker stop myfruit

# Remove container
docker rm myfruit

# View container stats
docker stats myfruit
```

### Push to Registry

```bash
# Login to Azure Container Registry
az acr login --name myregistry

# Tag image
docker tag fruitclassifier:latest myregistry.azurecr.io/fruitclassifier:v1.0

# Push to registry
docker push myregistry.azurecr.io/fruitclassifier:v1.0
```

## 🚀 Deploy to IoT Edge

### Prerequisites

- Azure IoT Hub
- IoT Edge device (Raspberry Pi, Jetson, VM, etc.)
- Docker running on edge device
- IoT Edge runtime installed

### Deployment Steps

#### 1. Update deployment.json

```json
{
  "modules": {
    "FruitClassifierFunction": {
      "settings": {
        "image": "myregistry.azurecr.io/fruitclassifier:v1.0",
        ...
      }
    }
  }
}
```

#### 2. Deploy to Device

```bash
# Using Azure CLI
az iot edge deployment create \
  --deployment-id fruitclassifier-v1 \
  --hub-name my-iot-hub \
  --target-condition "deviceId='my-edge-device'" \
  --content deployment.json \
  --priority 100

# Or using Azure Portal
# IoT Hub → IoT Edge → Create Deployment
```

#### 3. Verify Deployment

```bash
# SSH into edge device
ssh your-edge-device

# Check module status
docker ps | grep fruitclassifier

# View module logs
docker logs -f FruitClassifierFunction

# Get module stats
docker stats FruitClassifierFunction
```

## 🧪 Testing Examples

### Python Test Script

```python
import requests
import json

EDGE_DEVICE_URL = "http://localhost:8000"

# Test health
response = requests.get(f"{EDGE_DEVICE_URL}/health")
print("Health:", response.json())

# Test classification
payload = {
    "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "fruit_type": "apple",
    "device_id": "camera-01"
}

response = requests.post(
    f"{EDGE_DEVICE_URL}/classify",
    json=payload,
    headers={"Content-Type": "application/json"}
)
print("Classification:", response.json())
```

### PowerShell Test Script

```powershell
$url = "http://localhost:8000"

# Health check
$health = curl.exe -s "$url/health" | ConvertFrom-Json
Write-Host "Health: $($health.status)"

# Classification
$payload = @{
    image_data = "iVBORw0KGgo..."
    fruit_type = "apple"
    device_id = "camera-01"
} | ConvertTo-Json

$response = curl.exe -s -X POST "$url/classify" `
    -H "Content-Type: application/json" `
    -d $payload | ConvertFrom-Json

Write-Host "Prediction: $($response.prediction)"
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `docker: command not found` | Install Docker Desktop or Docker Engine |
| Container exits immediately | Check logs: `docker logs container-name` |
| Port already in use | Change port: `docker run -p 9000:8000` |
| Cannot connect to container | Check if running: `docker ps` |
| High memory usage | Reduce container resources or add limits |
| Slow image build | Use BuildKit: `DOCKER_BUILDKIT=1 docker build .` |

### View Error Logs

```bash
# Real-time logs
docker logs -f fruitclassifier-test

# Last 50 lines
docker logs --tail 50 fruitclassifier-test

# With timestamps
docker logs -t fruitclassifier-test

# Since specific time
docker logs --since 2m fruitclassifier-test
```

## 📊 Performance Tips

1. **Use slim images**: `python:3.9-slim` vs `python:3.9` (140MB vs 280MB)
2. **Multi-stage builds**: Reduce final image size
3. **Minimize layers**: Combine RUN commands
4. **Use .dockerignore**: Exclude unnecessary files
5. **Resource limits**: `docker run --memory=256m --cpus=1`

## 🔐 Security Best Practices

✅ **Implemented**:
- Non-root user in container
- Health checks for monitoring
- Minimal base image (slim variant)
- No hardcoded credentials

⚠️ **For Production**:
- Use private container registry
- Scan images for vulnerabilities: `az acr scan`
- Enable logging and monitoring
- Use secrets management (Azure Key Vault)
- Implement network security policies

## 📚 Additional Resources

- Docker Documentation: https://docs.docker.com
- Azure IoT Edge: https://learn.microsoft.com/en-us/azure/iot-edge
- Container Best Practices: https://docs.docker.com/develop/dev-best-practices
- IoT Edge Deployment: https://learn.microsoft.com/en-us/azure/iot-edge/how-to-deploy-modules-portal

---

**Status**: ✅ Ready for deployment  
**Time to complete**: 10-20 minutes  
**Difficulty**: Intermediate  
**Key Skills**: Docker, Containerization, IoT Edge, Deployment  
