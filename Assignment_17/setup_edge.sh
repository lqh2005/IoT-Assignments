#!/bin/bash

# Setup script for Azure Function on IoT Edge
# Builds and tests the containerized function

echo "🚀 Azure Function on IoT Edge - Setup Script"
echo "=============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Docker installation
echo -e "\n${YELLOW}Step 1: Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not installed. Install Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker installed$(docker --version)${NC}"

# Step 2: Build Docker image
echo -e "\n${YELLOW}Step 2: Building Docker image...${NC}"
docker build -t fruitclassifier:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Failed to build Docker image${NC}"
    exit 1
fi

# Step 3: Test image locally
echo -e "\n${YELLOW}Step 3: Testing container locally...${NC}"

# Stop any existing container
docker stop fruitclassifier-test 2>/dev/null

# Run container in background
docker run -d --name fruitclassifier-test -p 8000:8000 fruitclassifier:latest

# Wait for container to start
sleep 3

# Health check
echo -e "\n${YELLOW}Running health check...${NC}"
HEALTH_STATUS=$(curl -s http://localhost:8000/health | grep -c "healthy")

if [ $HEALTH_STATUS -eq 1 ]; then
    echo -e "${GREEN}✅ Container health check passed${NC}"
else
    echo -e "${RED}❌ Container health check failed${NC}"
    docker logs fruitclassifier-test
    docker stop fruitclassifier-test
    exit 1
fi

# Step 4: Test classification endpoint
echo -e "\n${YELLOW}Step 4: Testing /classify endpoint...${NC}"

TEST_PAYLOAD='{
  "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "fruit_type": "apple",
  "device_id": "test-device-01"
}'

RESPONSE=$(curl -s -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d "$TEST_PAYLOAD")

echo "Response: $RESPONSE"

if echo "$RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✅ Classification endpoint working${NC}"
else
    echo -e "${RED}❌ Classification endpoint test failed${NC}"
fi

# Step 5: Test IoT event processing
echo -e "\n${YELLOW}Step 5: Testing /process-iot-event endpoint...${NC}"

IOT_PAYLOAD='{
  "device_id": "sensor-01",
  "sensor_data": {
    "temperature": 22.5,
    "humidity": 65,
    "ripeness": "ripe"
  },
  "timestamp": "2026-05-04T10:30:45Z"
}'

RESPONSE=$(curl -s -X POST http://localhost:8000/process-iot-event \
  -H "Content-Type: application/json" \
  -d "$IOT_PAYLOAD")

echo "Response: $RESPONSE"

if echo "$RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✅ IoT event endpoint working${NC}"
else
    echo -e "${RED}❌ IoT event endpoint test failed${NC}"
fi

# Step 6: Get statistics
echo -e "\n${YELLOW}Step 6: Checking function statistics...${NC}"

STATS=$(curl -s http://localhost:8000/stats)
echo "Statistics: $STATS"

# Cleanup
echo -e "\n${YELLOW}Cleaning up test container...${NC}"
docker stop fruitclassifier-test
docker rm fruitclassifier-test

echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Push image to registry: docker push <registry>/fruitclassifier:latest"
echo "2. Update deployment.json with correct image URI"
echo "3. Deploy to IoT Edge: az iot edge deployment create ..."
echo "4. Monitor deployment: az iot edge deployment show ..."
