# Setup script for Azure Function on IoT Edge (Windows PowerShell)
# Builds and tests the containerized function

Write-Host "🚀 Azure Function on IoT Edge - Setup Script (Windows)" -ForegroundColor Green
Write-Host "=============================================================" -ForegroundColor Green

# Step 1: Check Docker installation
Write-Host "`nStep 1: Checking Docker..." -ForegroundColor Yellow

try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not installed. Install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Step 2: Build Docker image
Write-Host "`nStep 2: Building Docker image..." -ForegroundColor Yellow
docker build -t fruitclassifier:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
    exit 1
}

# Step 3: Test image locally
Write-Host "`nStep 3: Testing container locally..." -ForegroundColor Yellow

# Stop any existing container
docker stop fruitclassifier-test 2>$null
docker rm fruitclassifier-test 2>$null

# Run container in background
Write-Host "Starting container..." -ForegroundColor Cyan
docker run -d --name fruitclassifier-test -p 8000:8000 fruitclassifier:latest

# Wait for container to start
Start-Sleep -Seconds 3

# Health check
Write-Host "`nRunning health check..." -ForegroundColor Cyan

$healthResponse = curl.exe -s http://localhost:8000/health

if ($healthResponse | Select-String "healthy") {
    Write-Host "✅ Container health check passed" -ForegroundColor Green
} else {
    Write-Host "❌ Container health check failed" -ForegroundColor Red
    docker logs fruitclassifier-test
    docker stop fruitclassifier-test
    exit 1
}

# Step 4: Test classification endpoint
Write-Host "`nStep 4: Testing /classify endpoint..." -ForegroundColor Yellow

$testPayload = @{
    image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    fruit_type = "apple"
    device_id = "test-device-01"
} | ConvertTo-Json

$response = curl.exe -s -X POST http://localhost:8000/classify `
    -H "Content-Type: application/json" `
    -d $testPayload

Write-Host "Response: $response" -ForegroundColor Cyan

if ($response | Select-String "success") {
    Write-Host "✅ Classification endpoint working" -ForegroundColor Green
} else {
    Write-Host "❌ Classification endpoint test failed" -ForegroundColor Red
}

# Step 5: Test IoT event processing
Write-Host "`nStep 5: Testing /process-iot-event endpoint..." -ForegroundColor Yellow

$iotPayload = @{
    device_id = "sensor-01"
    sensor_data = @{
        temperature = 22.5
        humidity = 65
        ripeness = "ripe"
    }
    timestamp = "2026-05-04T10:30:45Z"
} | ConvertTo-Json

$response = curl.exe -s -X POST http://localhost:8000/process-iot-event `
    -H "Content-Type: application/json" `
    -d $iotPayload

Write-Host "Response: $response" -ForegroundColor Cyan

if ($response | Select-String "success") {
    Write-Host "✅ IoT event endpoint working" -ForegroundColor Green
} else {
    Write-Host "❌ IoT event endpoint test failed" -ForegroundColor Red
}

# Step 6: Get statistics
Write-Host "`nStep 6: Checking function statistics..." -ForegroundColor Yellow

$stats = curl.exe -s http://localhost:8000/stats
Write-Host "Statistics: $stats" -ForegroundColor Cyan

# Cleanup
Write-Host "`nCleaning up test container..." -ForegroundColor Yellow
docker stop fruitclassifier-test
docker rm fruitclassifier-test

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Push image to registry: docker push <registry>/fruitclassifier:latest"
Write-Host "2. Update deployment.json with correct image URI"
Write-Host "3. Deploy to IoT Edge: az iot edge deployment create ..."
Write-Host "4. Monitor deployment: az iot edge deployment show ..."
